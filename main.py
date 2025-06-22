import streamlit as st
import json
import os
from openai import OpenAI, OpenAIError

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🏋️ Hybrid Training AI Bot with Feedback Loop")

STORAGE_FILE = "plan_feedback_store.json"

def load_history():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(STORAGE_FILE, "w") as f:
        json.dump(history, f)

history = load_history()

weekly_sessions = st.number_input("How many sessions can you commit to in a week?", min_value=1, max_value=10, value=5)
experience = st.selectbox("Your training experience:", ["Beginner", "Intermediate", "Advanced"])
cycles = st.number_input("How many 3-week cycles do you want?", min_value=1, max_value=6, value=1)
goals = st.text_area("Your training goals:", "Build muscle and run a half marathon")

def generate_plan(prompt, model_name="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        st.warning(f"Model failed with error: {e}")
        return None

def build_prompt():
    memory = ""
    # Add last 2 plans + feedback for context
    for i, item in enumerate(history[-2:], 1):
        plan = item.get("plan", "")
        feedback = item.get("feedback", "")
        memory += f"Previous Plan {i}:\n{plan}\nUser Feedback: {feedback}\n\n"

    base_prompt = f"""
You are a hybrid coach blending Max El-Hag, Nick DiMarco, and an elite running coach.
Use this prior context to improve the next training plan:

{memory}

Create {cycles} training cycles (3 weeks each) based on experience '{experience}', weekly sessions {weekly_sessions}, and goals: {goals}.
Each week:
- Monday: Upper Strength + Gymnastics
- Tuesday: Lower Body Bodybuilding + Heavy Olympic Lifting
- Wednesday: VO2Max + Threshold Running
- Thursday: Zone 2 Cardio or Mobility
- Friday: Light Olympic Lifting + Gymnastics + Accessories
- Saturday: Easy Z2 Run or Rest
- Sunday: Z2 Run

Include progression using volume, intensity, density, and complexity for strength and gymnastics.
Return a clear, easy-to-follow weekly plan.
"""
    return base_prompt

if "last_plan" not in st.session_state:
    st.session_state.last_plan = None
if "awaiting_feedback" not in st.session_state:
    st.session_state.awaiting_feedback = False

def generate_and_show_plan():
    prompt = build_prompt()
    plan = generate_plan(prompt)
    if plan:
        st.session_state.last_plan = plan
        st.session_state.awaiting_feedback = True
        st.experimental_rerun()
    else:
        st.error("Failed to generate plan.")

if st.button("Generate Program") and not st.session_state.awaiting_feedback:
    with st.spinner("Generating your plan..."):
        generate_and_show_plan()

if st.session_state.last_plan and st.session_state.awaiting_feedback:
    st.markdown("### Your Training Plan")
    st.markdown(st.session_state.last_plan)
    st.markdown("---")
    feedback = st.text_area("Please provide your feedback or suggestions about this plan:", key="feedback_input")
    if st.button("Submit Feedback"):
        if feedback.strip():
            # Save plan + feedback persistently
            history.append({"plan": st.session_state.last_plan, "feedback": feedback.strip()})
            save_history(history)
            st.success("Thank you for your feedback! Generating improved plan...")
            # Reset feedback input
            st.session_state.feedback_input = ""
            # Regenerate new plan immediately
            generate_and_show_plan()
        else:
            st.warning("Please enter feedback before submitting.")
