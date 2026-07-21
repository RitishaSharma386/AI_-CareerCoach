"""
File: ui/app.py
Owner: Member 5 — Gargi Choudhary
Function: Streamlit-based user interface for the AI Career Coach. Provides
          4 tabs: Resume Upload, Job Matching, Learning Roadmap, Cover Letter.
          All agent calls go through agent_orchestrator.py.
Location: ui/ folder — entry point: streamlit run ui/app.py
"""

import streamlit as st
import os
import sys
import traceback

# Add root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


try:
    from graph.graph import graph
    print("LOG: Successfully imported graph")
except Exception as e:
    print(f"LOG: CRITICAL IMPORT ERROR (graph): {e}")
    graph = None

try:
    from tool.tool_pdf_parser import extract_text
    print("LOG: Successfully imported extract_text")
except Exception as e:
    print(f"LOG: CRITICAL IMPORT ERROR (tool): {e}")
    extract_text = None

# --- HELPER TO SAVE PDF ---
def get_base_state():  
    """Returns a completely initialized AgentState."""
    return {
        "resume_text": "",
        "resume_json": {},
        "skills": [],
        "resume_embedding": [],
        "target_role": "",
        "raw_job_listings": [],
        "retrieved_chunks": [],
        "job_listings": [],
        "skill_gaps": [],
        "roadmap": "",
        "cover_letter": "",
        "user_query": "",
        "user_intent": "",
        "error": None
    }

def save_uploaded_file(uploaded_file):
    os.makedirs("data/rawFolder", exist_ok=True)
    file_path = os.path.join("data/rawFolder", "uploaded_resume.pdf")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- UI LAYOUT ---

with st.sidebar:
    st.header("⚙️ App Controls")
    if st.button("🔄 Start Over / Reset"):
        st.session_state.clear()
        st.rerun()
    
    st.info("Upload a resume to begin your AI Career Coaching journey!")

tab1, tab2, tab3, tab4 = st.tabs(["Upload PDF", "Find Jobs", "Roadmap", "Cover Letter"])

# Tab 1: PDF uploader widget
with tab1:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None and graph is not None:
        st.success(f"Successfully uploaded: {uploaded_file.name}")
        
        
        if st.button("Process Document"):
            with st.spinner("Extracting data from resume using AI..."):
                try:
                    # 1. Save and extract text
                    file_path = save_uploaded_file(uploaded_file)
                    resume_text = extract_text(file_path)
                    
                    # 2. Prepare the base state with the extracted text
                    state = get_base_state()
                    state.update({
                        "resume_text": resume_text,
                        "user_query": "full_analysis" 
                    })
                    
                    # 3. Invoke the graph
                    result_state = graph.invoke(state)
                    
                    # 4. Check for errors and display results
                    if result_state.get("error"):
                        st.error(f"Backend Error: {result_state['error']}")
                    else:
                        # Save state for other tabs
                        st.session_state["full_state"] = result_state
                        st.session_state["resume_data"] = result_state.get("resume_json", {})
                        st.session_state["skills"] = result_state.get("skills", [])
                        
                        st.success("Resume parsed successfully!")
                        
                        st.divider() 
                        st.subheader("Extraction Results")
                        skills_list = st.session_state["skills"]
                        skills_string = ", ".join(skills_list) if skills_list else "No skills identified."
                        st.write(f"**Identified Skills:** {skills_string}")
                        
                        with st.expander("View Full Parsed Resume Data"):
                            st.json(st.session_state["resume_data"])
                            
                except Exception as e:
                    st.error(f"UI Integration Crash: {e}")
                    st.code(traceback.format_exc())

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
                    try:
                        # Feed the previous state back into the graph, with a new intent
                        state_request = st.session_state["full_state"]
                        state_request["user_intent"] = "jobs"
                        state_request["target_role"] = target_role
                        state_request["error"] = None 
                        
                        result_state = graph.invoke(state_request)
                        
                        if result_state.get("error"):
                            st.error(f"Backend Error: {result_state['error']}")
                        else:
                            jobs = result_state.get("job_listings", [])
                            if not jobs:
                                st.warning("No jobs were found. Check your API key or try a different role.")
                            else:
                                # Save updated state
                                st.session_state["full_state"] = result_state
                                st.session_state["matched_jobs"] = result_state.get("job_listings", [])
                            
                                st.success("Found matching jobs!")
                                for job in st.session_state["matched_jobs"]:
                                    expander_title = f"{job.get('title', 'Job')} at {job.get('company', 'Company')} - {job.get('match_score', 'N/A')}"
                                    with st.expander(expander_title):
                                        st.write(f"**Matched Skills:** {', '.join(job.get('matched_skills', []))}")
                                        st.write(f"**Missing Skills:** {', '.join(job.get('missing_skills', []))}")
                    except Exception as e:
                        st.error(f"UI Integration Crash: {e}")

# Tab 3: Roadmap
with tab3:
    st.header("Career Roadmap")
    if "full_state" not in st.session_state:
        st.warning("Please upload your resume in the 'Upload PDF' tab first!")
    else:
        if st.button("Generate Roadmap"):
            with st.spinner("AI is generating your personalized learning roadmap..."):
                try:
                    state_request = st.session_state["full_state"]
                    state_request["user_intent"] = "roadmap"
                    state_request["error"] = None
                    
                    result_state = graph.invoke(state_request)
                    
                    if result_state.get("error"):
                        st.error(f"Backend Error: {result_state['error']}")
                    else:
                        
                        roadmap_text = result_state.get("roadmap", "")
                        
                        # Guard against empty strings or None
                        if not roadmap_text or not roadmap_text.strip():
                            st.error("The AI returned an empty response due to a rate limit or prompt failure. Please try again.")
                        else:
                      
                            roadmap_text = result_state.get("roadmap", "")
                        
                            if not roadmap_text or not roadmap_text.strip():
                                st.error("The AI returned an empty response due to a rate limit or prompt failure. Please try again.")
                            else:
                                st.session_state["full_state"].update(result_state)
                                st.success("Roadmap generated!")
                                st.markdown(roadmap_text)
                        
                except Exception as e:
                    st.error(f"UI Integration Crash: {e}")

# Tab 4: Cover Letter 
with tab4:
    st.header("Cover Letter Generator")
    if "matched_jobs" not in st.session_state or not st.session_state["matched_jobs"]:
        st.warning("Please complete 'Upload PDF' and 'Find Jobs' before generating a cover letter!")
    else:
        jobs = st.session_state["matched_jobs"]
        job_options = {f"{j.get('title', 'Job')} at {j.get('company', 'Unknown')}": j for j in jobs}
        
        selected_job_key = st.selectbox("Select a job for your cover letter:", options=list(job_options.keys()))
        
        if st.button("Generate Cover Letter"):
            with st.spinner("Writing your tailored cover letter..."):
                try:
                    state_request = st.session_state["full_state"]
                    state_request["user_intent"] = "cover_letter"
                    state_request["error"] = None
                    
                    # Pass ONLY the selected job 
                    selected_job = job_options[selected_job_key]
                    state_request["job_listings"] = [selected_job] 
                    
                    result_state = graph.invoke(state_request)
                    
                    if result_state.get("error"):
                        st.error(f"Backend Error: {result_state['error']}")
                    else:
                        cover_letter_text = result_state.get("cover_letter", "Failed to generate.")
                        st.success("Cover letter generated!")
                        st.markdown(cover_letter_text)
                        st.divider()
                        st.write("📋 **Copy to Clipboard:**")
                        st.code(cover_letter_text, language="markdown")
                except Exception as e:
                    st.error(f"UI Integration Crash: {e}")