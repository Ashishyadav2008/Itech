import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI
st.set_page_config(
    page_title="I-tech Chatbot",
    page_icon="🤖",
    layout="wide"
)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
KNOWLEDGE_BASE_FILE = DATA_DIR / "knowledge_base.json"
def load_knowledge_base():
    if KNOWLEDGE_BASE_FILE.exists():
        with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    default_kb = {
        "institute_name": "I-tech",
        "courses": [
            {
                "name": "Full Stack Web Development",
                "duration": "6 months",
                "fee": "₹40,000",
                "description": "HTML, CSS, JavaScript, React, Node.js, MongoDB"
            },
            {
                "name": "Data Science",
                "duration": "8 months",
                "fee": "₹60,000",
                "description": "Python, Machine Learning, AI, Power BI"
            }
        ],
        "placements": {
            "placement_rate": "100%",
            "average_package": "4–8 LPA"
        },
        "contact": {
            "phone": "+91-9876543210",
            "email": "admissions@itech.com",
            "address": "Tech City, India"
        }
    }
    with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
        json.dump(default_kb, f, indent=2, ensure_ascii=False)

    return default_kb
def get_selected_course(kb, course_name):
    for c in kb["courses"]:
        if c["name"] == course_name:
            return c
    return None
def create_system_prompt(kb, selected_course=None):
    base_prompt = f"""
You are a professional admission counselor AI for {kb['institute_name']}.
Rules:
- Be polite, clear and student-friendly
- Use English or Hinglish
- Do not invent information
"""
    if selected_course:
        return base_prompt + f"""

User has selected this course:
Course Name: {selected_course['name']}
Duration: {selected_course['duration']}
Fees: {selected_course['fee']}
Description: {selected_course['description']}

Instructions:
- Prioritize and recommend ONLY this course
- If user asks about another course, gently redirect
- Answer general institute questions normally
"""
    else:
        courses = "\n".join([f"- {c['name']}" for c in kb["courses"]])
        return base_prompt + f"""
Available Courses:
{courses}
Instructions:
- Answer general institute and course questions
- Encourage course selection for personalized guidance
"""
def get_ai_response(user_message, chat_history, knowledge_base):
    selected_course_name = st.session_state.get("selected_course")
    selected_course = None
    if selected_course_name:
        selected_course = get_selected_course(
            knowledge_base, selected_course_name
        )
    messages = [{
        "role": "system",
        "content": create_system_prompt(knowledge_base, selected_course)
    }]
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    messages.append({
        "role": "user",
        "content": user_message
    })
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        max_tokens=700
    )
    return response.choices[0].message.content
def main():
    st.title("🤖 I-tech Admission Assistant")
    knowledge_base = load_knowledge_base()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    course_names = [c["name"] for c in knowledge_base["courses"]]
    if "selected_course" not in st.session_state:
        st.session_state.selected_course = None
    selected = st.selectbox(
        "📘 (Optional) Select a course for personalized guidance",
        ["-- No Course Selected --"] + course_names
    )
    if selected != "-- No Course Selected --":
        st.session_state.selected_course = selected
    else:
        st.session_state.selected_course = None
    st.markdown("---")
    if not st.session_state.chat_history:
        st.info("👋 Welcome to I-tech! Ask anything about courses, fees, or placements.")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_input = st.chat_input("Ask your question...")
    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().isoformat()
        })
        with st.spinner("Thinking..."):
            reply = get_ai_response(
                user_input,
                st.session_state.chat_history[:-1],
                knowledge_base
            )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply,
            "time": datetime.now().isoformat()
        })
        st.rerun()
if __name__ == "__main__":
    main()