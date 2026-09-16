import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from pypdf import PdfReader


# ==========================================
# SETUP
# ==========================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key nahi mili. .env file check karo.")
    st.stop()

client = OpenAI(api_key=api_key)


# ==========================================
# PAGE
# ==========================================

st.title("CareerForge")

st.write("AI-Powered Career & Interview Preparation Platform")

st.subheader("AI Mock Interview")


# ==========================================
# SESSION STATE
# ==========================================

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = ""

if "evaluated" not in st.session_state:
    st.session_state.evaluated = False

if "history" not in st.session_state:
    st.session_state.history = []

if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = ""    

if "job_match_report" not in st.session_state:
    st.session_state.job_match_report = ""  

if st.session_state.job_match_report:

    st.subheader("🎯 CareerForge Job Match Report")

    st.write(st.session_state.job_match_report)


# ==========================================
# CANDIDATE INFORMATION
# ==========================================

name = st.text_input(
    "Enter your name",
    key="candidate_name"
)

role = st.selectbox(
    "Select your target job role",
    [
        "Data Analyst",
        "Software Developer",
        "Data Scientist",
        "Web Developer",
        "Business Analyst"
    ],
    key="target_role"
)

st.divider()

st.subheader("📄 Upload Your Resume")

resume_file = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"],
    key="resume_uploader"
)

if resume_file is not None:

    if st.button("Analyze My Resume", key="analyze_resume"):

        try:
            reader = PdfReader(resume_file)

            extracted_text = ""

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    extracted_text += text + "\n"

            if not extracted_text.strip():
                st.error("Resume se text read nahi ho paya.")
            else:

                st.session_state.resume_text = extracted_text

                resume_response = client.responses.create(
                    model="gpt-5.6-luna",

                    instructions="""
You are an expert resume reviewer for CareerForge.

Analyze the student's resume objectively.

Use this structure:

# RESUME ANALYSIS

PROFILE SUMMARY:
Briefly summarize the candidate.

EDUCATION:
Mention the education information found.

SKILLS:
List the important skills found.

PROJECTS:
List the projects found.

EXPERIENCE:
List work/internship experience found.

STRENGTHS:
- Point 1
- Point 2
- Point 3

AREAS TO IMPROVE:
- Point 1
- Point 2
- Point 3

MISSING OR WEAK AREAS FOR THE TARGET ROLE:
Mention skills or evidence that appear missing or weak.

RESUME TIPS:
Give 5 practical improvements.

Do not invent any information that is not present in the resume.
""",

                    input=f"""
Target job role:
{role}

Resume text:
{extracted_text}
"""
                )

                st.session_state.resume_analysis = (
                    resume_response.output_text
                )

                st.success("Resume analyzed successfully!")

        except Exception as e:
            st.error(f"Resume analysis error: {e}")

if st.session_state.resume_analysis:

    st.subheader("🎯 AI Resume Analysis")

    st.write(st.session_state.resume_analysis) 

    # ==========================================
# JOB MATCH & SKILL GAP ANALYZER
# ==========================================

st.divider()

st.subheader("💼 Find Your Suitable Job Roles")

if st.session_state.resume_text:

    if st.button("Find My Job Matches", key="job_match_button"):

        job_match_response = client.responses.create(
            model="gpt-5.6-luna",

            instructions="""
You are CareerForge, an AI career matching assistant.

Analyze the candidate's resume and target job role.

Your task is to identify suitable job roles based only on the
candidate's actual resume.

Do not invent skills, experience, projects, or qualifications.

Use this exact structure:

# JOB MATCH REPORT

TARGET ROLE:
Mention the selected target role.

SUITABLE JOB ROLES:
1. Role - short reason
2. Role - short reason
3. Role - short reason
4. Role - short reason
5. Role - short reason

SKILL MATCH:
List important skills the candidate already has.

SKILL GAPS:
List skills that appear missing or weak for the target role.

PRIORITY SKILLS TO LEARN:
Give the 5 most useful skills/topics to learn next.

APPLICATION READINESS:
Give a short explanation of what the candidate should improve
before applying.

PREPARATION PLAN:
Give a practical 30-day preparation plan.

Be factual and do not guarantee employment or salary.
""",

            input=f"""
Target job role:
{role}

Candidate resume:
{st.session_state.resume_text}

Resume analysis:
{st.session_state.resume_analysis}
"""
        )

        st.session_state.job_match_report = (
            job_match_response.output_text
        )

else:

    st.info("Upload and analyze your resume first.")          


# ==========================================
# START INTERVIEW
# ==========================================

# ==========================================
# START INTERVIEW
# ==========================================

if st.button("Start Interview", key="start_interview"):

    if not name:
        st.warning("Please enter your name.")

    elif not st.session_state.resume_text:
        st.warning("Please upload and analyze your resume first.")

    else:

        response = client.responses.create(
            model="gpt-5.6-luna",

            instructions=f"""
You are an AI job interviewer for CareerForge.

Candidate name: {name}
Target role: {role}

You have access to the candidate's resume.

Conduct a personalized interview based on:
- candidate's resume
- skills
- projects
- education
- target job role

Rules:
- Ask exactly ONE question.
- Make the question relevant to the candidate.
- Use the candidate's actual resume when possible.
- Do not invent any experience, skill, project, or qualification.
- Start with a natural opening question.
- Do not provide the answer.
- Wait for the candidate's response.
""",

            input=f"""
Candidate Resume:

{st.session_state.resume_text}

Start the interview with the first personalized question.
"""
        )

        st.session_state.interview_started = True
        st.session_state.question_number = 1
        st.session_state.current_question = response.output_text
        st.session_state.current_evaluation = ""
        st.session_state.evaluated = False
        st.session_state.history = []
        st.session_state.final_report = ""

        st.rerun()


# ==========================================
# INTERVIEW SCREEN
# ==========================================

if st.session_state.interview_started:

    st.write(
        f"### Question {st.session_state.question_number} of 5"
    )

    st.subheader("AI Interviewer")

    st.write(st.session_state.current_question)


    # Dynamic key = each question gets its own answer box
    answer_key = f"candidate_answer_{st.session_state.question_number}"

    answer = st.text_area(
        "Your Answer",
        key=answer_key,
        height=150
    )


    # ======================================
    # EVALUATE ANSWER
    # ======================================

    if not st.session_state.evaluated:

        if st.button(
            "Evaluate My Answer",
            key=f"evaluate_{st.session_state.question_number}"
        ):

            if not answer.strip():

                st.warning("Please enter your answer first.")

            else:

                evaluation_response = client.responses.create(
                    model="gpt-5.6-luna",

                    instructions="""
You are an expert job interview evaluator.

Evaluate the candidate's answer objectively.

Give the result in this exact structure:

SCORE: X/10

WHAT WAS GOOD:
- Point 1
- Point 2

WHAT CAN BE IMPROVED:
- Point 1
- Point 2

BETTER ANSWER:
Write a stronger sample answer.

INTERVIEWER FEEDBACK:
Give short and practical feedback.

Do not invent experience that the candidate did not mention.
""",

                    input=f"""
Target role: {role}

Interview question:
{st.session_state.current_question}

Candidate answer:
{answer}
"""
                )

                evaluation = evaluation_response.output_text

                st.session_state.current_evaluation = evaluation
                st.session_state.evaluated = True

                # Save interview data
                st.session_state.history.append(
                    {
                        "question_number":
                            st.session_state.question_number,

                        "question":
                            st.session_state.current_question,

                        "answer":
                            answer,

                        "evaluation":
                            evaluation
                    }
                )

                st.rerun()


    # ======================================
    # SHOW EVALUATION
    # ======================================

    if st.session_state.evaluated:

        st.subheader("AI Evaluation")

        st.write(st.session_state.current_evaluation)


        # ==================================
        # NEXT QUESTION
        # ==================================

        if st.session_state.question_number < 5:

            if st.button(
                "Next Question",
                key=f"next_{st.session_state.question_number}"
            ):

                next_question_response = client.responses.create(

                    model="gpt-5.6-luna",

                    instructions=f"""
You are conducting a professional job interview.

Candidate name: {name}
Target role: {role}

This is question number:
{st.session_state.question_number + 1} of 5.

Ask exactly ONE interview question.

Rules:
- Gradually increase difficulty.
- Keep it relevant to {role}.
- Build naturally from previous interview.
- Do not give the answer.
""",

                    input=f"""
Previous interview question:
{st.session_state.current_question}

Previous candidate answer:
{answer}

Previous evaluation:
{st.session_state.current_evaluation}

Ask the next interview question.
"""
                )

                st.session_state.question_number += 1

                st.session_state.current_question = (
                    next_question_response.output_text
                )

                st.session_state.current_evaluation = ""

                st.session_state.evaluated = False

                st.rerun()


        # ==================================
        # COMPLETE INTERVIEW
        # ==================================

        else:

            st.success("You have completed all 5 interview questions!")

            if st.button(
                "Generate Final Interview Report",
                key="final_report_button"
            ):

                interview_data = ""

                for item in st.session_state.history:

                    interview_data += f"""

QUESTION {item['question_number']}:
{item['question']}

CANDIDATE ANSWER:
{item['answer']}

EVALUATION:
{item['evaluation']}

-------------------------
"""


                final_response = client.responses.create(

                    model="gpt-5.6-luna",

                    instructions="""
You are a professional career coach.

Analyze the complete mock interview.

Create a final interview report.

Use this structure:

# FINAL INTERVIEW REPORT

OVERALL ASSESSMENT:
Give a short summary.

OVERALL SCORE:
Give a score out of 10.

STRENGTHS:
- Point 1
- Point 2
- Point 3

WEAK AREAS:
- Point 1
- Point 2
- Point 3

TECHNICAL READINESS:
Give a short assessment based only on the interview.

COMMUNICATION:
Give a short assessment based only on the answers.

IMPROVEMENT PLAN:
Give 5 specific things the candidate should practice.

FINAL ADVICE:
Give practical interview advice.

Do not invent qualifications or experience.
""",

                    input=f"""
Candidate:
{name}

Target role:
{role}

Complete interview:

{interview_data}
"""
                )

                st.session_state.final_report = (
                    final_response.output_text
                )

                st.rerun()


# ==========================================
# SHOW FINAL REPORT
# ==========================================

if st.session_state.final_report:

    st.divider()

    st.subheader("🎯 CareerForge Final Interview Report")

    st.write(st.session_state.final_report)