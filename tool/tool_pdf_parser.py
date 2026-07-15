"""
File: tool/tool_pdf_parser.py
Owner: Member 2 — Kashish Dhingra
Function: Extracts raw text from uploaded PDF resumes using pdfplumber.
          Handles multi-page documents.Warns when extracted text is too short and
          the PDF may be image-based.
Location: tool/ folder — called by task/task_extract_skills.py.
"""

import os
import pdfplumber

def extract_text(pdf_path: str) -> str:

    # Validate file type before attempting PDF parsing
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF resume files are supported.")

    # Check whether file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("Resume file not found.")

    # Store extracted text from all pages of the resume
    text = ""
    # Open PDF and process each page individually
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text available on the current page
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        # Warn if extracted text is less than 100 words (possible scanned/image PDF)
        if len(text.split()) < 100:
            print("Warning: PDF may be image-based")
        return text
    

if __name__ == "__main__":
    pdf_file = input("Enter PDF path: ")

    try:
        # Test PDF extraction independently
        extracted_text = extract_text(pdf_file)
        print(extracted_text)

    except Exception as e:
        print(e)