# AI_-CareerCoach

## Member 2 - Resume Agent

The Resume Agent handles resume processing in the initial stage of the AI Career Coach pipeline. It processes a user's resume and converts it into structured information that can be used by other agents.

### Resume Processing Flow

The resume processing workflow consists of extracting text from the uploaded PDF, converting the extracted text into structured resume information, generating embeddings, and storing the required details in the shared graph state.

## Implemented Components

### 1. PDF Parser (`tool/tool_pdf_parser.py`)

This module extracts text from uploaded resume PDFs using `pdfplumber`.

Implemented features:
- Extracts text from multi-page PDF resumes
- Validates that only PDF files are processed
- Handles pages where text extraction returns empty values
- Shows a warning when very little text is extracted, which can indicate an image-based/scanned resume

### 2. Resume Information Extraction (`task/task_extract_skills.py`)

This module converts extracted resume text into structured resume information using an LLM.

The extracted information includes:
- Name
- Skills
- Education
- Experience
- Projects
- Target Role

Additional handling:
- Missing fields are assigned default values to maintain a consistent JSON structure
- A fallback message is generated when no technical skills are detected

### 3. Resume Agent (`agent/agent_resume.py`)

The resume agent connects the parsing and extraction pipeline.

The `run(state)` function:
- Reads resume text from the shared state
- Generates structured resume JSON
- Generates resume embeddings
- Updates the graph state with:
  - `resume_json`
  - `skills`
  - `resume_embedding`

## Testing Done

The Resume Agent was tested on different resume formats, including:
- Single-column resumes
- Two-column resumes
- Resumes with tables
- Image-heavy resume layouts

Automated test cases were added in:

`tests/test_agent_resume.py`

The tests cover:
- JSON structure validation
- Empty skills fallback handling
- Skills format conversion
- Missing field handling
- Target role extraction

All implemented test cases are passing successfully.

## Known Limitations

- The pipeline is currently optimized for English resumes.
- Mixed language resumes may not always be extracted accurately.
- OCR support is not implemented, so fully image-based resumes may have limited extraction quality.
- Complex resume formatting can affect extracted text quality.