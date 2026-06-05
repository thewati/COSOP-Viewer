# COSOP-Viewer
IFAD COSOP Viewer extracts partners from COSOP PDFs and displays them. Upon clicking on the extracted partners, it navigates to the first appearance of the partner in the document

# Architecture
Frontend:
- React
- TypeScript
- React-PDF

Backend:
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
# Issues / Limitations
