"""
File: ui/app.py
Owner: Member 5 — Gargi Choudhary
Function: Streamlit-based user interface for the AI Career Coach. Provides
          4 tabs: Resume Upload, Job Matching, Learning Roadmap, Cover Letter.
          All agent calls go through agent_orchestrator.py.
Location: ui/ folder — entry point: streamlit run ui/app.py
"""

import streamlit as st
import time  #to stimulate delays

# --- MOCK BACKEND FUNCTIONS ---
def mock_extract_resume_data(file_bytes):
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0199",
        "skills": ["Python", "Streamlit", "Data Analysis", "Machine Learning", "Git"],
        "education": "B.Tech. Computer Science"
    }

def mock_agent_jobs(skills, target_role):
    time.sleep(1.5)  
    return [
        {
            "title": f"Senior {target_role}" if target_role else "Senior Developer",
            "company": "Tech Innovators Inc.",
            "match_score": "85%",
            "matched_skills": [skill for skill in skills if skill in ["Python", "Machine Learning"]],
            "missing_skills": ["Docker", "AWS", "FastAPI"]
        },
        {
            "title": f"{target_role} Engineer" if target_role else "Software Engineer",
            "company": "DataDriven Startup",
            "match_score": "72%",
            "matched_skills": [skill for skill in skills if skill in ["Streamlit", "Data Analysis", "Git"]],
            "missing_skills": ["Kubernetes", "PostgreSQL"]
        }
    ]

def mock_generate_roadmap():
    time.sleep(2.0)  
    return """
### 🗺️ Your Personalized Learning Roadmap
Based on your current skills and target role, here is your path forward:

#### Month 1: Cloud & Containerization
* **Docker Basics:** Learn to containerize your Streamlit apps.
* **AWS Fundamentals:** Deploy a simple app using AWS EC2 or Elastic Beanstalk.

#### Month 2: Advanced Backend
* **FastAPI:** Build robust APIs to serve your models.
* **Database Management:** Learn PostgreSQL for persistent data storage.
    """

def mock_generate_cover_letter(name, company, role):
    """Simulates AI writing a cover letter."""
    time.sleep(2.0)
    return f"""
Dear Hiring Manager at **{company}**,

I am writing to express my enthusiastic interest in the **{role}** position. 

With my robust background in Python, Streamlit, and Data Analysis, I have consistently driven technical excellence and delivered scalable solutions. I am eager to bring my passion for problem-solving to {company} and contribute to your team's innovative goals.

Thank you for your time and consideration.

Sincerely,
**{name}**
"""

tab1, tab2, tab3, tab4 = st.tabs(["Upload PDF", "Find Jobs", "Generate Roadmap", "Cover Letter"])

# Tab 1: PDF uploader widget
with tab1:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")
        file_bytes = uploaded_file.read()
        parsed_data = mock_extract_resume_data(file_bytes)
        st.session_state["resume_data"] = parsed_data
        
        st.divider() 
        st.subheader("Extraction Results")
        skills_string = ", ".join(parsed_data["skills"])
        st.write(f"**Identified Skills:** {skills_string}")
        
        with st.expander("View Full Parsed Resume Data"):
            st.json(parsed_data)

# Tab 2: Job Search
with tab2:
    st.header("Find Target Jobs")
    if "resume_data" not in st.session_state:
        st.warning("Please upload your resume in the 'Upload PDF' tab first!")
    else:
        target_role = st.text_input("Enter your target role (e.g., Data Scientist, Backend Engineer):")
        
        if st.button("Find Jobs"):
            if not target_role:
                st.error("Please enter a target role to search for.")
            else:
                with st.spinner("Agent is scouring the web for matching jobs..."):
                    user_skills = st.session_state["resume_data"]["skills"]
                    # SAVE TO SESSION STATE FOR TAB 4
                    st.session_state["matched_jobs"] = mock_agent_jobs(user_skills, target_role)
                
                st.success("Found matching jobs!")
                
                for job in st.session_state["matched_jobs"]:
                    expander_title = f"{job['title']} at {job['company']} - {job['match_score']} Match"
                    with st.expander(expander_title):
                        st.write(f"**Matched Skills:** {', '.join(job['matched_skills']) if job['matched_skills'] else 'None'}")
                        st.write(f"**Missing Skills:** {', '.join(job['missing_skills'])}")

# Tab 3: Roadmap
with tab3:
    st.header("Career Roadmap")
    if "resume_data" not in st.session_state:
        st.warning("Please upload your resume in the 'Upload PDF' tab first!")
    else:
        if st.button("Generate Roadmap"):
            with st.spinner("AI is generating your personalized learning roadmap..."):
                roadmap_markdown = mock_generate_roadmap()
            st.markdown(roadmap_markdown)

# Tab 4: Cover Letter 
with tab4:
    st.header("Cover Letter Generator")
    if "resume_data" not in st.session_state or "matched_jobs" not in st.session_state:
        st.warning("Please complete 'Upload PDF' and 'Find Jobs' before generating a cover letter!")
    else:
        jobs = st.session_state["matched_jobs"]
        job_options = {f"{j['title']} at {j['company']}": j for j in jobs}
        
        selected_job_key = st.selectbox("Select a job for your cover letter:", options=list(job_options.keys()))
        
        if st.button("Generate Cover Letter"):
            selected_job = job_options[selected_job_key]
            user_name = st.session_state["resume_data"]["name"]
            
            with st.spinner("Writing your tailored cover letter..."):
                cover_letter_text = mock_generate_cover_letter(
                    name=user_name, 
                    company=selected_job["company"], 
                    role=selected_job["title"]
                )
            
            st.success("Cover letter generated!")
            
            
            st.markdown(cover_letter_text)
            
            st.divider()
            st.write("📋 **Copy to Clipboard:**")
            st.code(cover_letter_text, language="markdown")