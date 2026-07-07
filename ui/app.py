"""
File: ui/app.py
Owner: Member 5 — Gargi Choudhary
Function: Streamlit-based user interface for the AI Career Coach. Provides
          4 tabs: Resume Upload, Job Matching, Learning Roadmap, Cover Letter.
          All agent calls go through agent_orchestrator.py.
Location: ui/ folder — entry point: streamlit run ui/app.py
"""
import streamlit as st

def mock_extract(file_bytes):
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


tab1, tab2, tab3, tab4 = st.tabs(["Upload PDF", "Tab 2", "Tab 3", "Tab 4"])

with tab1:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")
        
        file_bytes = uploaded_file.read()
        
        parsed_data = mock_extract(file_bytes)
        
        st.session_state["resume_data"] = parsed_data
        
        st.divider() 
        
        st.subheader("Extraction Results")
        
        skills_string = ", ".join(parsed_data["skills"])
        st.write(f"**Identified Skills:** {skills_string}")
        
        with st.expander("View Full Parsed Resume Data"):
            st.json(parsed_data)

with tab2:
    st.write("Coming soon")
    if "resume_data" in st.session_state:
        st.info(f"Session State Active! We still remember the name is: {st.session_state['resume_data']['name']}")

with tab3:
    st.write("Coming soon")

with tab4:
    st.write("Coming soon")