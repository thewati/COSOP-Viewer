from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import fitz
import tempfile
import os
import json
import requests

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from groq import Groq
import re

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(
    api_key=HF_TOKEN
)

# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODEL_URL = (
#     "https://router.huggingface.co/"
#     "hf-inference/models/"
#     "Qwen/Qwen2.5-7B-Instruct"
# )

# print("MODEL_URL =", MODEL_URL)

# headers = {
#     "Authorization": f"Bearer {HF_TOKEN}"
# }


def query_llm(prompt: str):
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=250
        )

        # response = client.chat.completions.create(
        # model="llama-3.1-8b-instant",
        # messages=[
        #     {
        #         "role": "user",
        #         "content": prompt
        #     }
        # ],
        # temperature=0,
        # max_tokens=250
        # )

        print(response)

        return response

    except Exception as e:
        print("HF ERROR:")
        print(str(e))

        return {
            "error": str(e)
        }


def clean_name(name):
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def find_first_page(name, pages):
    search_name = clean_name(name)
    for p in pages:
        if search_name.lower() in p["text"].lower():
            return p["page"]

    return None


def chunk_text(text, chunk_size=5000): #reduced from 15,000
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end

    return chunks


@app.get("/")
def home():
    return {"message": "COSOP Viewer API"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    # Saving temp PDF
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    # Opening PDF
    doc = fitz.open(temp_path)

    pages = []
    full_text = ""

    for page_num in range(len(doc)):

        page = doc.load_page(page_num)

        text = page.get_text()

        pages.append({
            "page": page_num + 1,
            "text": text
        })

        full_text += f"\nPAGE {page_num+1}\n{text}"

    text_chunks = chunk_text(full_text)

    all_partners = []

    for chunk_number, chunk in enumerate(text_chunks[:3]):
        print(
            f"Processing chunk "
            f"{chunk_number + 1}/{len(text_chunks)}"
        )

        prompt = f"""
        You are an AI assistant extracting IFAD partners from a COSOP document.

        Your task is to identify organizations that IFAD works with,
        collaborates with, coordinates with, co-finances with,
        implements projects with, or explicitly identifies as partners.

        Rules:
        - Return ONLY valid JSON
        - No explanation
        - No markdown
        - No extra text

        An IFAD partner may include:
        - Ministries
        - Government agencies
        - NGOs
        - UN agencies
        - Development banks
        - Financial institutions
        - Bilateral donors
        - International organizations
        - Research institutions
        - Private sector organizations
        - Farmer organizations
        - Civil society organizations
        
        Do NOT return:
        - projects
        - programmes
        - policies
        - strategies
        - countries
        - geographic regions
        - IFAD itself

        Important:
        - Extract ONLY organizations that appear to have a partnership,
        implementation, financing, coordination,
        advisory, or collaboration role.
        - Do NOT include IFAD.
        - Do NOT include countries.

        JSON format:
        [
        {{
            "name": "...",
            "category": "..."
        }}
        ]

        COSOP TEXT:
        {chunk}
        """

        llm_response = query_llm(prompt)

        if (
            isinstance(llm_response, dict)
            and llm_response.get("error")
        ):
            continue

        generated = (
            llm_response
            .choices[0]
            .message
            .content
        )

        json_start = generated.find("[")
        json_end = generated.rfind("]") + 1

        json_text = generated[json_start:json_end]

        try:

            partners = json.loads(json_text)

            all_partners.extend(partners)

        except Exception:

            print(
                f"Failed parsing chunk "
                f"{chunk_number + 1}"
            )

    # Extract generated text
    if isinstance(llm_response, dict) and llm_response.get("error"):

        return {
            "partners": [],
            "llm_error": llm_response
        }

    generated = llm_response.choices[0].message.content

    # Try extracting JSON portion
    json_start = generated.find("[")
    json_end = generated.rfind("]") + 1

    json_text = generated[json_start:json_end]

    try:
        partners = json.loads(json_text)

    except Exception:
        partners = all_partners
        unique = {}

        for partner in partners:
            name = partner["name"].strip()
            if name not in unique:
                unique[name] = partner

        partners = list(unique.values())

    # Adding page numbers
    for partner in partners:

        page = find_first_page(
            partner["name"],
            pages
        )

        partner["page"] = page

    doc.close()
    os.unlink(temp_path)

    return {
        "partners": partners
    }