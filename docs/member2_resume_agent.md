# Member 2 — Resume Agent

## Responsibility

I worked on the Resume Agent module of the AI Career Coach project.

The main responsibilities of this module are:
- Extracting text from uploaded resume PDFs
- Converting unstructured resume text into structured information
- Extracting skills, projects, education, and other resume details using an LLM
- Generating resume embeddings for matching with relevant job descriptions

---

# Components

## 1. tool/tool_pdf_parser.py

This file handles the extraction of text from resume PDFs.

It uses `pdfplumber` to read PDF files and extract text from different pages.

### Main Function

`extract_text(pdf_path: str)`

### Work done:
- Reads the uploaded resume PDF
- Extracts text from all available pages
- Supports different resume layouts
- Displays a warning when very little text is extracted, as the PDF may contain scanned images instead of actual text

### Input:
Resume PDF path

### Output:
Extracted raw resume text

---

## 2. task/task_extract_skills.py

This file is responsible for converting extracted resume text into structured resume data.

The extracted text is sent to the LLM, which returns important resume details in JSON format.

### Main Function

`extract_resume_info(raw_text: str)`

### Information extracted:
- Name
- Skills
- Education
- Experience
- Projects
- Target Role

### Target Role Extraction

If the resume already contains a target role, it is extracted directly.

If the role is not mentioned, the model identifies a suitable entry-level role based on:
- Skills
- Projects
- Degree specialization
- Technologies

For example:
- Python, C++, and software projects → Software Engineer Intern
- Python, Machine Learning, and AI projects → Machine Learning Engineer Intern

### Output Structure

```json
{
    "name": "",
    "skills": [],
    "experience": [],
    "education": [],
    "projects": [],
    "target_role": ""
}