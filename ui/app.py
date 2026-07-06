"""
File: ui/app.py
Owner: Member 5 — Gargi Choudhary
Function: Streamlit-based user interface for the AI Career Coach. Provides
          4 tabs: Resume Upload, Job Matching, Learning Roadmap, Cover Letter.
          All agent calls go through agent_orchestrator.py.
Location: ui/ folder — entry point: streamlit run ui/app.py
"""
import streamlit as st

tab1, tab2, tab3, tab4 = st.tabs(["Upload PDF", "Tab 2", "Tab 3", "Tab 4"])

with tab1:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")

with tab2:
    st.write("Coming soon")

with tab3:
    st.write("Coming soon")

with tab4:
    st.write("Coming soon")
