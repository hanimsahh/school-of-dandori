import ast
import json
import os
import re
import time
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st
from openai import OpenAI

# =========================================================
# PAGE SETUP & WELLBEING THEME
# =========================================================
st.markdown("""
<div style="text-align:center;">
<iframe src="https://lottie.host/embed/42fb9e10-dbad-4a6f-8eb2-2263a6cdc2b4/xYOZwx81cZ.lottie"
style="width:600px;height:200px;border:none;"></iframe>
</div>
""", unsafe_allow_html=True)


st.set_page_config(page_title="School of Dandori | Sanctuary", layout="wide", page_icon="🌿")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Quicksand', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F0F2F0 0%, #E6EBE0 100%);
}

/* Headings */
h1, h2, h3 {
    color: #344E41;
    font-weight: 500;
}

/* Custom Cards for Courses */
.course-card {
    background-color: rgba(255, 255, 255, 0.7);
    padding: 24px;
    border-radius: 20px;
    border: 1px solid rgba(163, 177, 138, 0.2);
    box-shadow: 0 10px 30px rgba(0,0,0,0.03);
    margin-bottom: 20px;
}

/* Wellbeing Buttons */
.stButton>button {
    background-color: #A3B18A;
    color: white;
    border-radius: 25px;
    border: none;
    padding: 0.6em 2em;
    font-weight: 500;
}

.stButton>button:hover {
    background-color: #588157;
    color: white;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CONFIG & DATA
# =========================================================

# DANDORI WELLBEING QUESTIONS
QUESTIONS = [
    "How are you feeling today? What kind of energy are you looking to cultivate?",
    "Are you looking for a solitary, quiet experience or something social and collaborative?",
    "Do you prefer working with your hands (tactile) or engaging your mind (intellectual)?",
    "What is your ideal 'pace' for learning—slow and steady, or intensive and focused?",
    "Is there a specific skill you've been curious to nurture (e.g., mindfulness, craft, focus)?",
    "How much time/energy are you able to invest in this journey right now?",
    "Would you prefer a rustic, nature-based setting or a refined indoor studio?",
    "Finally, is there any specific atmosphere or subject you'd like to avoid today?"
]

# =========================================================
# MOCK DATA LOADER (Matching your Course Data)
# =========================================================

@st.cache_data
def load_dandori_data():
    import sqlite3
    import os

    db_path = os.path.join(os.path.dirname(__file__), "../../database/db.sqlite")
    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query("SELECT * FROM courses", conn)
    conn.close()

    df = df.rename(columns={
        'file': 'Class ID',
        'title': 'Title',
        'instructor': 'Instructor',
        'location': 'Location',
        'cost': 'Cost'
    })

    if 'Type' not in df.columns:
        df['Type'] = 'Wellbeing'
    if 'Description' not in df.columns:
        df['Description'] = df['Title'].apply(lambda x: f"A mindful journey into {x.lower()}. Reconnect with your creative spirit.")
    if 'Skills' not in df.columns:
        df['Skills'] = df.apply(lambda x: ['Mindfulness', 'Creativity', 'Presence'], axis=1)

    df['text_blob'] = df.apply(lambda row: f"{row['Title']} {row['Description']} {', '.join(row['Skills'])} {row['Type']}".lower(), axis=1)

    return df

# =========================================================
# OPENROUTER INTEGRATION
# =========================================================


def get_openrouter_client():
    if "OPENROUTER_API_KEY" not in st.secrets:
        st.error("OpenRouter API key not found. Set OPENROUTER_API_KEY in .streamlit/secrets.toml")
        st.stop()

    return OpenAI(
        api_key=st.secrets["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )


def interview_to_course_criteria(qa_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    transcript = "\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs])

    prompt = f"""
You are a wellbeing guide for 'The School of Dandori'.
Convert this interview into structured course selection criteria.

Return ONLY valid JSON with keys:
{{
  "preferred_types": [string],
  "focus_skills": [string],
  "mood_intent": string,
  "max_cost": number,
  "preferred_setting": "Nature" | "Studio" | "Either",
  "pace_preference": "Slow" | "Intensive" | "Either",
  "reasoning_summary": string
}}

Interview:
{transcript}
""".strip()

    client = get_openrouter_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for generating course selection criteria."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    text = response.choices[0].message.content

    try:
        return json.loads(text)
    except Exception as e:
        st.warning("Could not parse JSON criteria from model; using defaults.")
        return {
            "preferred_types": [],
            "focus_skills": [],
            "mood_intent": "",
            "max_cost": 200,
            "preferred_setting": "Either",
            "pace_preference": "Either",
            "reasoning_summary": ""
        }


def recommend_courses(criteria: Dict[str, Any], df: pd.DataFrame) -> str:
    def matches(r):
        if criteria.get("max_cost"):
            if r.get("Cost", 0) > criteria["max_cost"]:
                return False
        if criteria.get("preferred_setting") and criteria["preferred_setting"] != "Either":
            if str(r.get("Setting", "")).lower() != str(criteria["preferred_setting"]).lower():
                return False
        if criteria.get("preferred_types"):
            if len(criteria["preferred_types"]) > 0 and str(r.get("Type", "")).lower() not in [x.lower() for x in criteria["preferred_types"]]:
                return False
        return True

    filtered = df[df.apply(matches, axis=1)]
    if filtered.empty:
        filtered = df

    top_courses = filtered.head(5)

    course_overview = "\n".join(
        [f"- {row['Title']} ({row['Location']}, £{row['Cost']}): {row['Description']}" for _, row in top_courses.iterrows()]
    )

    prompt = f"""
You are Arthur, a calm and thoughtful guide from the School of Dandori.
Based on this criteria:
{json.dumps(criteria, indent=2)}

Please recommend the top 3 courses from the list below with brief rationale for each.

Course options:
{course_overview}
"""

    client = get_openrouter_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an empathetic course recommender."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250
    )

    return response.choices[0].message.content


# =========================================================
# SESSION STATE & UI
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Welcome to the Sanctuary. Let's find a path that suits your soul.\n\n" + QUESTIONS[0]
        }
    ]

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "qa_pairs" not in st.session_state:
    st.session_state.qa_pairs = []

if "criteria" not in st.session_state:
    st.session_state.criteria = None


# ═══════════════════════════════════════════════════════════════════

st.title("🍃 The School of Dandori")
st.subheader("Personalised Path Finder")

df = load_dandori_data()

# Avatar (GIF version)
ARTHUR_AVATAR = "robot.gif"

# ═══════════════════════════════════════════════════════════════════

for msg in st.session_state.chat_history:
    if msg["role"] == "assistant":
        with st.chat_message("assistant", avatar=ARTHUR_AVATAR):
            st.markdown(msg["content"])
    else:
        with st.chat_message("user"):
            st.write(msg["content"])


# ═══════════════════════════════════════════════════════════════════
# USER INPUT
# ═══════════════════════════════════════════════════════════════════
user_input = st.chat_input("Share your thoughts...")

if user_input:
    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # 🧠 QUESTION FLOW
    if st.session_state.criteria is None:

        current_q = QUESTIONS[st.session_state.question_index]
        st.session_state.qa_pairs.append((current_q, user_input))
        st.session_state.question_index += 1

        # ➡️ Ask next question
        if st.session_state.question_index < len(QUESTIONS):
            next_q = QUESTIONS[st.session_state.question_index]

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": next_q
            })

        # ✅ Finished questions → recommend
        else:
            st.session_state.criteria = interview_to_course_criteria(
                st.session_state.qa_pairs
            )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Thank you. I'm reflecting on your answers to find the right path for you..."
            })

            recommendation_text = recommend_courses(
                st.session_state.criteria, df
            )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": recommendation_text
            })

    # 🔄 Rerun to refresh chat immediately
    st.rerun()
# (...) any other content here as needed
