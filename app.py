from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from utils import input_pdf_setup

load_dotenv()

# Configure gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

if "candidates" not in st.session_state:
    st.session_state.candidates = []

#Function to get response from gemini
def get_gemini_response(input, pdf_content, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], job_description])
    return response.text

#Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#Create a reusable Geimini chat model
def get_gemini_chat_model():
    return genai.GenerativeModel('gemini-1.5-flash').start_chat(history=st.session_state.chat_history)



    
## Streamlit APP
st.set_page_config(page_title="ATS Resume Expert", layout="wide")
st.header("ATS Resume Asisstant for Recruiters")

#CSS for better UI
st.markdown("""
    <style>
    .chat-box {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        height: 500px;
        overflow-y: auto;
        font-size: 14px;
        border: 1px solid #ddd;
    }
    .chat-message {
        margin-bottom: 10px;
    }
    .chat-user {
        font-weight: bold;
        color: #3366cc;
    }
    .chat-ai {
        font-weight: bold;
        color: #009966;
    }
    </style>
""", unsafe_allow_html=True)


#Create two columns (75%, 25%)
left_col, right_col = st.columns([2, 2])

with left_col:
    #Input
    input_text = st.text_area("Paste Job Description:", key="input")
    uploaded_file = st.file_uploader("Upload your resume(PDF only)", type=["pdf"])

    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")

    #Tabs for features
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧾 Resume Review", "📈 Skill Improvement", "📊 Match %", "📉 Skill Gap Analyzer", "📊 Recruiter Dashboard"])

    #Prompts
    prompt_resume_review = """
    You are an experienced HR with Tech Experience in the field of Data Science, Full Stack Web development, Big Data Engineering, DEVOPS, Data Analyst ,Machine Learning Engineer and AI Engnieer your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """
    prompt_skill_improve = """
    You are an experienced HR with Tech Experience in the field of Data Science, Full Stack Web development, Big Data Engineering, DEVOPS, Data Analyst ,Machine Learning Engineer and AI Engnieer your task is to provide the information about how to improve my skills which are lacking in the provided resume against the job description. 
    Please provide the professional information of improvement of how the candidate can enhance thier skills which are they lacking in his/her resume. """

    prompt_match_percent = """
    You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science, Full Stack Web development, Big Data Engineering, DEVOPS, Data Analyst,Machine Learning Engineer, AI Engnieer and deep ATS functionality, 
    your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches the job description. First the output should come as percentage and then keywords missing and last final thoughts.
    """

    gap_prompt = """
    You are a technical recruiter with AI expertise. Given this job description and resume:
    1. Identify the top missing skills, tools, or certifications in the resume.
    2. For each missing skill, suggest how to learn or improve it (courses, tools, projects, certifications).
    Output should be in bullet points with clarity and conciseness.
    """

    #Tab 1 Resume Review
    with tab1:
        if st.button("🔍 Analyze Resume"):
            if uploaded_file and input_text:
                with st.spinner("Analyzing Resume..."):
                    pdf_content = input_pdf_setup(uploaded_file)
                    result = get_gemini_response(prompt_resume_review, pdf_content, input_text)
                    st.subheader("🧾 Review Result")
                    st.write(result)
            else:
                st.warning("Please upload the resume and enter job description.")
    #Tab 2: Skill Improvement
    with tab2:
        if st.button("📈 Suggest Skill Improvements"):
            if uploaded_file and input_text:
                with st.spinner("Checking skills...."):
                    pdf_content = input_pdf_setup(uploaded_file)
                    response = get_gemini_response(prompt_skill_improve, pdf_content, input_text)
                    st.subheader("📌 Recommendations")
                    st.write(response)
            else:
                st.warning("Please upload a resume and enter job description.")

    #Tab3: Match Percentage
    with tab3:
        if st.button("📊 Show Match %"):
            if uploaded_file and input_text:
                with st.spinner("Calculating match..."):
                    pdf_content = input_pdf_setup(uploaded_file)
                    response = get_gemini_response(prompt_match_percent, pdf_content, input_text)
                    st.subheader("📉 Match Result")
                    st.write(response)
                    
                    #Extract percentage from result
                    match_percentage = "N/A"
                    for line in response.splitlines():
                        if "%" in line:
                            match_percentage = line.strip()
                            break
                    
                    #Save to session state
                    st.session_state.candidates.append({
                        "Name": uploaded_file.name,
                        "Match": match_percentage,
                        "Review": response
                    })


            else:
                st.warning("Please upload a resume and enter job description.")
    #tab 4
    with tab4:
        st.subheader("📉 Skill Gap Analyzer")
        if uploaded_file and input_text:
            if st.button("🔍 Analyze Skill Gaps"):
                with st.spinner("Analyzing..."):
                    pdf_content = input_pdf_setup(uploaded_file)
                    gap_result = get_gemini_response(gap_prompt, pdf_content, input_text)
                    
                    st.markdown("**🛠️ Missing Skills & Recommendations:**")
                    st.write(gap_result)

                    if st.session_state.candidates:
                        st.session_state.candidates[-1]['skill gap'] = gap_result

        else:
            st.info("Please upload a resume and enter a job description.")


    # Tab 5
    with tab5:
        st.subheader("📊 Candidate Tracker")

        if not st.session_state.candidates:
            st.info("No candidates analyzed yet.")
        else:
            for idx, candidate in enumerate(st.session_state.candidates):
                with st.expander(f"📄 {candidate['Name']} - {candidate['Match']}"):
                    st.markdown("**Match Percentage:**")
                    st.write(candidate['Match'])
                    st.markdown("**Review:**")
                    st.write(candidate['Review'])

with right_col:
    st.subheader("💬 Resume Chatbot (Ask AI about the Resume)")

    with st.expander("🧠 Ask Questions About the Resume", expanded=True):
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Check resume and job description
        if uploaded_file and input_text:
            question = st.text_input("Ask anything (e.g., Does this candidate have ML experience?)", key="chat_question")

            if st.button("Ask", key="chat_ask"):
                with st.spinner("Thinking..."):
                    pdf_content = input_pdf_setup(uploaded_file)
                    model = get_gemini_chat_model()

                    response = model.send_message([
                        "You are a helpful recruiting assistant. Use this resume and job description to answer:",
                        pdf_content[0],
                        input_text,
                        question
                    ])

                    st.session_state.chat_history.append({"role": "user", "parts": [question]})
                    st.session_state.chat_history.append({"role": "model", "parts": [response.text]})

        else:
            st.info("📄 Please upload a resume and provide the job description to begin chatting.")

        # Display chat history as plain text
        if st.session_state.chat_history:
            st.markdown("### 🕑 Chat History")
            for msg in st.session_state.chat_history:
                role = "🧑 You" if msg["role"] == "user" else "🤖 Gemini"
                st.markdown(f"**{role}:** {msg['parts'][0]}")
