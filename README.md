# COSOP-Viewer
IFAD COSOP Viewer extracts partners from COSOP PDFs and displays them. Upon clicking on the extracted partners, it navigates to the first appearance of the partner in the document

# Architecture
### Frontend:
- React
- TypeScript
- React-PDF

### Backend:
- FastAPI
- PyMuPDF
- Hugging Face / Groq LLM

# Repository Structure
- backend/
  - env.example
  - main.py
  - requirements.txt
- frontend/
  - public/
    - pdf.worker.min.mjs
  - src/
    - App.css
    - App.tsx
- screenshots/
  - ...
  - ...


# Installation
Start by cloning this repo in your terminal through the command `git clone https://github.com/thewati/COSOP-Viewer`
### Backend  
Enter the following commands in your terminal:
1. Navigate to your backend folder `cd backend`
2. Create a virtual environment using `python -m venv myvenv` where `myvenv` is the name of your new virtual environment
3. Activate the virtual environment using `source myvenv/bin/activate` (or `myvenv\Scripts\activate` on Windows)
4. Install requirements using `pip install -r requirements.txt`
5. Make a copy of the sample ".env.example" file using `cp .env.example .env`
6. Open your new `.env` file and add your API Key/Access Token. Please note that you only need one between Hugging face and Groq
    - COSOP-Viewer uses Hugging Face by default. If you are using Hugging Face, find `HF_TOKEN=HUGGING_FACE_TOKEN_PLACEHOLDER` in the file and replace "HUGGING_FACE_TOKEN_PLACEHOLDER" with your actual API Key. If you don't have an Access Token, please create an account, navigate to `Settings / Access Tokens` and create an Access Token with "Read" permissions on: https://huggingface.co/
    - If you are using Groq, find `GROQ_API_KEY=GROQ_API_KEY_PLACEHOLDER` in the file and replace "GROQ_API_KEY_PLACEHOLDER" with your actual API Key. If you don't have an API Key, please create an account and create an API Key on: https://console.groq.com/home. Please note that you will need to make modifications to the code in order to work with Groq. More on this in the "Issues / Limitations" sections
7. Run your backend using `uvicorn main:app --reload`

### Frontend
Open another terminal and Enter the following commands. Make sure the backend terminal from the previous section is still running:
1. Navigate to your frontend folder `cd frontend`
2. Download and install the necessary dependencies using `npm install`
3. Run your frontend using `npm run dev`

# Screenshots
## Uploading PDF
## Clickable List of Partners
## Automatic Navigation

# Issues / Limitations
- Currently only the first 5 pages are rendered in the PDF viewer for performance during development.
- Due to API inference quota contraints, I used Groq llama-3.1-8b-instant temporarily to continue improving accuracy of the COSOP-Viewer.The COSOP-Viewer works with Hugging Face by default. If you want to use Groq, then
  - Get a Groq API Key and update the .env file accordingly. This was expained in the "Installation" section
  - Comment out this section and uncomment so that your code client looks as below
  - In main.py, comment out this section and uncomment so that your code looks as seen below inside query_llm() function
    
- Page references are based on chunk-level extraction.
