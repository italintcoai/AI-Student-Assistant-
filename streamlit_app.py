import streamlit as st
import requests
import json
import os

# --- Configuration ---
# Access the Gemini API Key securely from Streamlit secrets
# In Streamlit Cloud, you'll set this under 'Secrets' (e.g., API_KEY="YOUR_GEMINI_API_KEY")
# For local testing, you can create a .streamlit/secrets.toml file:
# API_KEY = "YOUR_GEMINI_API_KEY"
try:
    GEMINI_API_KEY = st.secrets["API_KEY"]
except FileNotFoundError:
    st.error("API Key not found. Please set 'API_KEY' in your Streamlit secrets or in .streamlit/secrets.toml for local development.")
    st.stop()
except KeyError:
    st.error("API Key not found. Please set 'API_KEY' in your Streamlit secrets or in .streamlit/secrets.toml for local development.")
    st.stop()


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- Function to call the Gemini API ---
def call_gemini_api(prompt):
    """
    Sends a prompt to the Gemini API and returns the text response.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'key': GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        with st.spinner("AI is thinking..."):
            response = requests.post(GEMINI_API_URL, headers=headers, params=params, data=json.dumps(payload))
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            result = response.json()

            if result.get('candidates') and len(result['candidates']) > 0 and \
               result['candidates'][0].get('content') and \
               result['candidates'][0]['content'].get('parts') and \
               len(result['candidates'][0]['content']['parts']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error(f"Unexpected API response structure: {result}")
                return "Error: Could not get a valid response from AI. Please try again."
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API: {e}. Please check your API key and network connection.")
        return "Error: Failed to connect to AI. Please check your network or API key."
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON response: {e}. Invalid JSON response from AI.")
        return "Error: Invalid JSON response from AI."

# --- Initialize Streamlit Session State ---
# This ensures variables persist across reruns
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
    st.session_state.problem_statement = ""
    st.session_state.ai_generated_questions = ""
    st.session_state.user_answers_to_questions = ""
    st.session_state.supporting_events = ""
    st.session_state.final_solution = ""
    st.session_state.final_feedback = ""
    st.session_state.error_message = ""

# --- Callbacks for Navigation ---
def next_step():
    st.session_state.current_step += 1
    st.session_state.error_message = "" # Clear error on step change

def set_error_message(message):
    st.session_state.error_message = message

def restart_app():
    st.session_state.current_step = 1
    st.session_state.problem_statement = ""
    st.session_state.ai_generated_questions = ""
    st.session_state.user_answers_to_questions = ""
    st.session_state.supporting_events = ""
    st.session_state.final_solution = ""
    st.session_state.final_feedback = ""
    st.session_state.error_message = ""

# --- Application Layout ---
st.set_page_config(layout="centered", page_title="Structured AI Problem-Solver")

st.title("🧠 Structured AI Problem-Solver")
st.markdown("A step-by-step assistant to help students **define, understand, and solve problems** with AI guidance.")
st.markdown("---")

if st.session_state.error_message:
    st.error(st.session_state.error_message)

# --- Step 1: Identify Your Problem ---
if st.session_state.current_step == 1:
    st.header("Step 1: Identify Your Problem")
    st.write("Start by clearly stating the problem or challenge you are facing. Being as specific as possible helps the AI.")

    st.session_state.problem_statement = st.text_area(
        "My Problem Is:",
        value=st.session_state.problem_statement,
        height=150,
        placeholder="e.g., I'm consistently late submitting my assignments because I procrastinate.",
        key="problem_input" # Unique key for text_area
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Submit Problem & Get Questions", key="submit_problem_btn"):
            if not st.session_state.problem_statement.strip():
                set_error_message("Please describe your problem to proceed.")
            else:
                prompt_questions = f"""As a student, I have the following problem: "{st.session_state.problem_statement}". To help me understand this problem better and find a solution, please ask me 3-5 concise, insightful follow-up questions. Format them as a numbered list."""
                ai_response = call_gemini_api(prompt_questions)
                if "Error" not in ai_response:
                    st.session_state.ai_generated_questions = ai_response
                    next_step()
    with col2:
        st.markdown(
            """
            <div style="padding: 10px; background-color: #e0f2f7; border-radius: 8px;">
                <small><strong>Skill Development Tip:</strong> Articulating a problem clearly is the first step to solving it. This step helps you practice precision in articulation.</small>
            </div>
            """, unsafe_allow_html=True
        )


# --- Step 2: Brainstorm for Understanding (AI asks questions) ---
elif st.session_state.current_step == 2:
    st.header("Step 2: Brainstorm for Understanding")
    st.write("The AI has generated some questions to help you think more deeply about your problem. Please answer them to provide more context.")

    st.subheader("AI's Clarifying Questions:")
    st.info(st.session_state.ai_generated_questions)

    st.session_state.user_answers_to_questions = st.text_area(
        "Your Answers:",
        value=st.session_state.user_answers_to_questions,
        height=200,
        placeholder="Provide detailed answers to the AI's questions here. Make sure to address each question.",
        key="answers_input"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Continue to Events", key="continue_events_btn"):
            if not st.session_state.user_answers_to_questions.strip():
                set_error_message("Please answer the questions to proceed.")
            else:
                next_step()
    with col2:
        st.markdown(
            """
            <div style="padding: 10px; background-color: #e0f2f7; border-radius: 8px;">
                <small><strong>Skill Development Tip:</strong> Answering probing questions enhances your analytical and self-reflection skills, leading to a deeper understanding of the root cause.</small>
            </div>
            """, unsafe_allow_html=True
        )


# --- Step 3: Provide Supporting Events ---
elif st.session_state.current_step == 3:
    st.header("Step 3: Provide Supporting Events/Context")
    st.write("Describe specific events, scenarios, or situations where this problem occurs or is particularly noticeable. This helps the AI understand the real-world context.")

    st.session_state.supporting_events = st.text_area(
        "Relevant Events/Details:",
        value=st.session_state.supporting_events,
        height=200,
        placeholder="e.g., Last week, I missed a deadline because I spent hours on social media instead of studying. | I often feel overwhelmed when I have multiple assignments due in the same week.",
        key="events_input"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Get Solution & Feedback", key="get_solution_btn"):
            if not st.session_state.supporting_events.strip():
                set_error_message("Please provide some relevant events or details to proceed.")
            else:
                # Consolidate all information for the final AI call
                full_context_prompt = f"""As a student, I need help solving a problem. Here's a structured overview of my situation:

Problem: "{st.session_state.problem_statement}"

My answers to follow-up questions that clarify the problem:
"{st.session_state.user_answers_to_questions}"

Relevant events or specific details that happened:
"{st.session_state.supporting_events}"

Based on ALL this information, please do two things:
1. Provide a clear, actionable solution or a set of steps to address my problem.
2. Provide constructive feedback on my overall understanding of the problem and the clarity of the information I provided, suggesting how I could further refine my problem-solving approach in the future.
Format your response clearly with 'Solution:' and 'Feedback:' headings."""

                ai_response_full = call_gemini_api(full_context_prompt)

                # Attempt to parse solution and feedback
                if "Solution:" in ai_response_full and "Feedback:" in ai_response_full:
                    parts = ai_response_full.split("Solution:", 1)
                    solution_part = parts[1] if len(parts) > 1 else ""

                    if "Feedback:" in solution_part:
                        solution_text = solution_part.split("Feedback:", 1)[0].strip()
                        feedback_text = solution_part.split("Feedback:", 1)[1].strip()
                    else: # Fallback if Feedback is not after Solution
                        solution_text = solution_part.strip()
                        feedback_text = "No explicit 'Feedback:' section found after solution."

                    st.session_state.final_solution = solution_text
                    st.session_state.final_feedback = feedback_text
                else:
                    # Fallback if AI doesn't use the exact headings
                    st.session_state.final_solution = "Could not parse specific solution/feedback sections. Full AI response:\n" + ai_response_full
                    st.session_state.final_feedback = ""

                next_step()
    with col2:
        st.markdown(
            """
            <div style="padding: 10px; background-color: #e0f2f7; border-radius: 8px;">
                <small><strong>Skill Development Tip:</strong> Providing concrete examples strengthens your ability to identify patterns and specific triggers related to a problem.</small>
            </div>
            """, unsafe_allow_html=True
        )

# --- Step 4: Solution and Feedback ---
elif st.session_state.current_step == 4:
    st.header("Step 4: AI's Solution & Feedback")
    st.write("Based on all the information you provided, here is the AI's suggested solution and feedback on your problem-solving process.")

    if st.session_state.final_solution:
        st.subheader("Suggested Solution:")
        st.markdown(st.session_state.final_solution)
        st.markdown(
            """
            <div style="padding: 10px; background-color: #e6ffe6; border-radius: 8px; border: 1px solid #c6ffc6;">
                <small><strong>Skill Development Tip:</strong> Evaluate this solution. Is it realistic for your situation? What are the first three steps you would take to implement it? This develops your practical implementation skills.</small>
            </div>
            """, unsafe_allow_html=True
        )

    if st.session_state.final_feedback:
        st.subheader("Feedback on Your Process:")
        st.markdown(st.session_state.final_feedback)
        st.markdown(
            """
            <div style="padding: 10px; background-color: #fffacd; border-radius: 8px; border: 1px solid #ffe8b6;">
                <small><strong>Skill Development Tip:</strong> Reflect on the feedback. What did you do well in defining the problem? What could you improve in your next problem-solving attempt? Continuous self-assessment is key to mastery.</small>
            </div>
            """, unsafe_allow_html=True
        )

    st.button("Start New Problem", on_click=restart_app, key="restart_btn")
