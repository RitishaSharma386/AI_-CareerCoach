"""
File: tool/tool_pdf_parser.py
Owner: Member 2 — Kashish Dhingra
Function: Extracts raw text from uploaded PDF resumes using pdfplumber.
          Handles multi-page documents. Raises error for image-based PDFs.
Location: tool/ folder — called by task/task_extract_skills.py.
"""

import pdfplumber

def extract_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if len(text.strip()) < 100:
            raise ValueError("PDF appears image-based")
        return text
    

if __name__ == "__main__":
    pdf_file = input("Enter PDF path: ")

    try:
        extracted_text = extract_text(pdf_file)
        print(extracted_text)

    except Exception as e:
        print(e)