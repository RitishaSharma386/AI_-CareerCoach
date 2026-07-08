"""
File: ui/app.py
Owner: Member 5 — Gargi Choudhary
Function: Streamlit-based user interface for the AI Career Coach. Provides
          4 tabs: Resume Upload, Job Matching, Learning Roadmap, Cover Letter.
          All agent calls go through agent_orchestrator.py.
Location: ui/ folder — entry point: streamlit run ui/app.py
"""

import streamlit as st
import time  # Added to simulate delays so we can see the loading spinners

# --- MOCK BACKEND FUNCTION ---
def mock_extract_resume_data(file_bytes):
    """
    Simulates reading a PDF and returning extracted data.
    In the future, this will be replaced with real PDF parsing logic.
    """
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0199",
        "skills": ["Python", "Streamlit", "Data Analysis", "Machine Learning", "Git"],
        "education": "B.Tech. Computer Science"
    }

def mock_agent_jobs(skills, target_role):
    """Simulates an AI agent finding jobs based on skills and role."""
    time.sleep(1.5)  # Simulate a slow API call
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
    """Simulates generating a Markdown roadmap."""
    time.sleep(2.0)  # Simulate slow AI generation
    return """
### Your Personalized Learning Roadmap
Based on your current skills and target role, here is your path forward:

#### Month 1: Cloud & Containerization
* **Docker Basics:** Learn to containerize your Streamlit apps.
* **AWS Fundamentals:** Deploy a simple app using AWS EC2 or Elastic Beanstalk.

#### Month 2: Advanced Backend
* **FastAPI:** Build robust APIs to serve your models.
* **Database Management:** Learn PostgreSQL for persistent data storage.
    """

# Set up the 4-tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Upload PDF", "Find Jobs", "Generate Roadmap", "Tab 4"])

# Tab 1: PDF uploader widget
with tab1:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")
        
        file_bytes = uploaded_file.read()
        
        parsed_data = mock_extract_resume_data(file_bytes)
        
        # Store in session state for use across other tabs
        st.session_state["resume_data"] = parsed_data
        
        st.divider() 
        
        st.subheader("Extraction Results")
        
        skills_string = ", ".join(parsed_data["skills"])
        st.write(f"**Identified Skills:** {skills_string}")
        
        with st.expander("View Full Parsed Resume Data"):
            st.json(parsed_data)

# Tabs 2-4: Placeholder text & Session State check
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
                    jobs = mock_agent_jobs(user_skills, target_role)
                
                st.success("Found matching jobs!")
                
                for job in jobs:
                    expander_title = f"{job['title']} at {job['company']} - {job['match_score']} Match"
                    with st.expander(expander_title):
                        st.write(f"**Matched Skills:** {', '.join(job['matched_skills']) if job['matched_skills'] else 'None'}")
                        st.write(f"**Missing Skills:** {', '.join(job['missing_skills'])}")

with tab3:
    st.header("Career Roadmap")
    if "resume_data" not in st.session_state:
        st.warning("Please upload your resume in the 'Upload PDF' tab first!")
    else:
        if st.button("Generate Roadmap"):
            with st.spinner("AI is generating your personalized learning roadmap..."):
                roadmap_markdown = mock_generate_roadmap()
            
            st.markdown(roadmap_markdown)

with tab4:
    st.write("Coming soon")
