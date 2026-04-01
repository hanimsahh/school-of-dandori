import json
import os
import re
import time
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
from openai import OpenAI

# =========================================================
# PAGE CONFIG (must be first Streamlit call)
# =========================================================
st.set_page_config(
    page_title="School of Dandori | Sanctuary",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE INIT (must happen before any rendering)
# =========================================================
for key, default in {
    "chat_history":             None,
    "api_history":              [],
    "question_index":           0,
    "qa_pairs":                 [],
    "criteria":                 None,
    "recommendations_rendered": False,
    "raw_recommendations":      None,
    "booking_step":             None,
    "booking_course":           None,
    "booking_details":          {},
    "booked_courses":           [],
    "panel_open":               False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================
# DYNAMIC CSS — panel open/closed controls layout
# =========================================================
panel_open   = st.session_state.panel_open
PANEL_W      = 260   # px
margin_right  = f"{PANEL_W + 24}px" if panel_open else "auto"
btn_label    = "✕ Close bookings" if panel_open else "🌿 My Bookings"
booked_count = len(st.session_state.get("booked_courses", []))
if booked_count > 0 and not panel_open:
    btn_label = f"🌿 My Bookings ({booked_count})"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600&display=swap');

:root {{
    --ink:       #344E41;
    --parchment: #F0F2F0;
    --sage:      #A3B18A;
    --moss:      #588157;
    --mist:      #A3B18A;
    --cream:     #E6EBE0;
    --warm-gray: #6B7C6B;
}}

html, body, [class*="css"] {{
    font-family: 'Quicksand', sans-serif;
    background-color: var(--parchment);
    color: var(--ink);
}}
.stApp {{
    background: linear-gradient(180deg, #F0F2F0 0%, #E6EBE0 100%);
}}

/* ── Hide Streamlit chrome & native sidebar ── */
#MainMenu, footer, header                  {{ display: block !important; }}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"]                  {{ display: block !important; }}

/* ── Main content block shifts when panel is open ── */
.block-container {{
    padding-top: 2rem !important;
    max-width: 860px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    transition: margin-left 0.3s ease;
}}


/* Style the toggle button specifically */
button#toggle-btn,
div[data-testid="stButton"]:first-of-type > button {{
    background: white !important;
    color: #588157 !important;
    border: 1.5px solid #A3B18A !important;
    border-radius: 10px !important;
    font-family: 'Quicksand', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    padding: 0.35rem 0.9rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09) !important;
    white-space: nowrap !important;
    min-width: unset !important;
}}
div[data-testid="stButton"]:first-of-type > button:hover {{
    background: #588157 !important;
    color: white !important;
    border-color: #588157 !important;
}}

/* ── Bookings panel ── */
.bookings-panel {{
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    width: {PANEL_W}px;
    background: white;
    border-left: 1px solid #A3B18A;
    padding: 4.5rem 1rem 1.5rem 1rem;
    overflow-y: auto;
    z-index: 2000;
    font-family: 'Quicksand', sans-serif;
    box-sizing: border-box;
    box-shadow: 4px 0 20px rgba(0,0,0,0.06);
    pointer-events: auto;   
}}
.bookings-panel-title {{
    font-size: 1rem;
    font-weight: 700;
    color: #344E41;
    margin-bottom: 0.2rem;
}}
.bookings-panel-sub {{
    font-size: 0.7rem;
    color: #6B7C6B;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #A3B18A;
    padding-bottom: 0.8rem;
    margin-bottom: 1rem;
}}
.bookings-empty {{
    font-size: 0.78rem;
    color: #9A9490;
    text-align: center;
    padding: 2rem 0.5rem;
    line-height: 1.8;
}}
.booking-item {{
    background: #F7FAF5;
    border: 1px solid #C8D5C2;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.71rem;
    color: #6B7C6B;
    line-height: 1.9;
}}
.booking-item-title {{
    font-size: 0.83rem;
    font-weight: 700;
    color: #344E41;
    margin-bottom: 0.4rem;
}}
.booking-item-cost {{
    font-size: 0.7rem;
    color: #588157;
    font-weight: 700;
    margin-top: 0.4rem;
}}

/* ── Header ── */
.sanctuary-header {{
    text-align: center;
    padding: 0.6rem 0 0.8rem;
    border-bottom: 1px solid var(--mist);
    margin-bottom: 2rem;
}}
.sanctuary-header .wordmark {{
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--moss);
    margin-bottom: 0.1rem;
}}
.sanctuary-header .subtitle {{
    font-size: 0.75rem;
    color: var(--warm-gray);
    letter-spacing: 0.14em;
    margin-top: 0.2rem;
}}

/* ── Progress sidebar ── */
.progress-sidebar {{
    position: fixed;
    left: 1.2rem;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
    z-index: 100;
}}
.progress-step {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    position: relative;
    width: 28px;
}}
.progress-circle {{
    width: 26px; height: 26px;
    border-radius: 50%;
    background: white;
    border: 2px solid var(--mist);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.62rem;
    font-weight: 700;
    color: var(--warm-gray);
    transition: all 0.3s;
    flex-shrink: 0;
}}
.progress-circle.done   {{ background: var(--sage); border-color: var(--sage); color: white; }}
.progress-circle.active {{
    background: var(--moss); border-color: var(--moss); color: white;
    box-shadow: 0 0 0 4px rgba(88,129,87,0.15);
}}
.progress-line      {{ width: 2px; height: 20px; background: var(--mist); margin-left: 13px; }}
.progress-line.done {{ background: var(--sage); }}
.progress-row       {{ display: flex; align-items: center; gap: 8px; }}
.progress-label     {{ font-size: 0.65rem; color: var(--warm-gray); white-space: nowrap; font-weight: 500; line-height: 26px; }}
.progress-label.active {{ color: var(--moss); font-weight: 700; }}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.2rem 0 !important;
}}
div[data-testid="stChatMessageContent"] p {{
    font-size: 0.95rem; line-height: 1.8; color: var(--ink);
}}
[data-testid="stChatMessage"]:has([alt="user"]) div[data-testid="stChatMessageContent"] {{
    background: var(--cream) !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 0.8rem 1.2rem !important;
    border: 1px solid var(--mist) !important;
    max-width: 85%; margin-left: auto;
}}
[data-testid="stChatMessage"]:has([alt="assistant"]) div[data-testid="stChatMessageContent"] {{
    background: white !important;
    border-radius: 4px 16px 16px 16px !important;
    padding: 1rem 1.4rem !important;
    border: 1px solid rgba(163,177,138,0.4) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    max-width: 90%;
}}
[data-testid="stChatMessage"] img {{ border-radius: 50%; border: 2px solid var(--mist); }}


#bookings-toggle-btn .stButton > button {{
    background: white !important;
    color: #588157 !important;
    border: 1.5px solid #A3B18A !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    padding: 0.35rem 0.9rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09) !important;
    min-width: unset !important;
}}
#bookings-toggle-btn .stButton > button:hover {{
    background: #588157 !important;
    color: white !important;
    border-color: #588157 !important;
}}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {{
    font-size: 0.9rem !important;
    background: white !important;
    border: 1px solid var(--mist) !important;
    border-radius: 14px !important;
    color: var(--ink) !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 3px rgba(163,177,138,0.2) !important;
}}

/* ── Course cards ── */
.course-card {{
    background: white;
    border: 1px solid var(--mist);
    border-radius: 18px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
}}
.course-card:hover {{ box-shadow: 0 8px 32px rgba(0,0,0,0.08); }}
.course-card .title {{ font-size: 1rem; font-weight: 700; color: var(--moss); margin-bottom: 0.2rem; }}
.course-card .meta  {{ font-size: 0.74rem; color: var(--warm-gray); letter-spacing: 0.04em; }}
.course-card .desc  {{ font-size: 0.86rem; color: #4A4845; margin-top: 0.5rem; line-height: 1.7; }}

/* ── Streamlit buttons (general) ── */
.stButton > button {{
    background-color: #A3B18A !important;
    color: white !important;
    border-radius: 25px !important;
    border: none !important;
    padding: 0.5em 1.2em !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    white-space: nowrap !important;
    min-width: 80px !important;
    transition: background-color 0.2s !important;
}}
.stButton > button:hover {{ background-color: #588157 !important; }}

/* ── Policy notice ── */
.policy-notice {{
    background: #FFF8F0;
    border: 1px solid #E8C99A;
    border-left: 4px solid #D4A853;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.8rem; color: #7A5C38;
    line-height: 1.8; margin: 1rem 0 1.5rem;
}}
.policy-notice strong {{ color: #5C3D1E; }}

/* ── Typing indicator ── */
.typing-indicator {{
    display: flex; gap: 5px;
    padding: 0.9rem 1.2rem;
    background: white;
    border-radius: 4px 16px 16px 16px;
    width: fit-content;
    border: 1px solid rgba(163,177,138,0.4);
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    margin-bottom: 0.5rem;
}}
.typing-indicator span {{
    width: 7px; height: 7px;
    background: var(--mist); border-radius: 50%;
    animation: bounce 1.2s infinite;
}}
.typing-indicator span:nth-child(2) {{ animation-delay: 0.2s; }}
.typing-indicator span:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes bounce {{
    0%, 80%, 100% {{ transform: translateY(0); background: var(--mist); }}
    40%           {{ transform: translateY(-6px); background: var(--sage); }}
}}


</style>
""", unsafe_allow_html=True)


# =========================================================
# TOGGLE BUTTON — rendered as a real Streamlit button
# Placed first so it floats at top-left via CSS
# =========================================================
st.markdown('<div id="bookings-toggle-btn">', unsafe_allow_html=True)
if st.button(btn_label, key="panel_toggle"):
    st.session_state.panel_open = not st.session_state.panel_open
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# BOOKINGS PANEL HTML — only injected when open
# =========================================================
if panel_open:
    booked = st.session_state.get("booked_courses", [])

    if not booked:
        items_html = '<div class="bookings-empty">No bookings yet.<br>Browse the recommendations<br>and reserve a course.</div>'
    else:
        items_html = ""
        for b in booked:
            items_html += (
                '<div class="booking-item">'
                '<div class="booking-item-title">' + b["course"]["title"] + '</div>'
                '&#128205; ' + b["course"]["location"] + '<br>'
                '&#128197; ' + b["details"]["date"] + '<br>'
                '&#128101; ' + str(b["details"]["participants"]) + ' person(s)<br>'
                '&#128179; ' + b["details"]["payment"] +
                '<div class="booking-item-cost">' + b["course"]["cost"] + '</div>'
                '</div>'
            )

    st.markdown(
        '<div class="bookings-panel">'
        '<div class="bookings-panel-title">&#127807; My Bookings</div>'
        '<div class="bookings-panel-sub">Your reserved courses</div>'
        + items_html +
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# SYSTEM PROMPTS
# =========================================================
ARTHUR_SYSTEM = """You are Arthur — the quiet, thoughtful guide at The School of Dandori.

Your personality:
- Warm but never gushing. Calm, unhurried, deeply present.
- You speak in short, considered sentences. You leave space for the person.
- You genuinely listen. You echo small details from what they've shared.
- Occasionally, you use gentle metaphors from nature or craft.
- You NEVER sound like a chatbot, a customer service rep, or a life coach.

STRICT RULES:
- You MUST end your response by asking EXACTLY this question (woven in naturally): {next_question}
- Do NOT invent your own question. Do NOT ask anything else.
- If someone says "recommend", "skip", "just tell me" or similar — acknowledge warmly, do not ask the question, just say you have enough to go on.
- Keep total response under 60 words.
- Be human. Be real."""

ARTHUR_RECOMMENDATION_SYSTEM = """You are Arthur from The School of Dandori.

Based on a person's intake answers, you are presenting 3 course recommendations.

The person's preferences (as JSON):
{criteria}

The person is based near: {location}
Prioritise courses geographically close to them. If none are close, acknowledge the distance warmly.

Available courses:
{courses}

Write a warm, personal message (3-4 sentences) that reflects what you heard, then introduce 3 courses.

Format (no markdown, no stars):

COURSE_1: [Title] | [Location] | £[Cost]
WHY_1: [One sentence why this fits THEM specifically]

COURSE_2: [Title] | [Location] | £[Cost]
WHY_2: [One sentence why this fits THEM specifically]

COURSE_3: [Title] | [Location] | £[Cost]
WHY_3: [One sentence why this fits THEM specifically]

Be Arthur. Be warm. Be brief."""

# =========================================================
# QUESTIONS & CONFIG
# =========================================================
QUESTIONS = [
    "How are you doing today?",
    "Good to know. Whereabouts are you based? Even just a town or city helps me point you somewhere you can actually get to.",
    "What's drawing you here — are you looking to learn something new, slow down and be present, or try something completely different?",
    "Would you rather work with your hands and make something tangible, or engage your mind through ideas, movement, or conversation?",
    "How much time can you give to this — a single afternoon, a full day, or something you'd return to weekly?",
    "Last one — is there anything you'd rather avoid? A type of setting, a mood, or something that just doesn't feel right today."
]
STEP_LABELS     = ["Hello", "Location", "Intent", "Style", "Time", "Avoid"]
TOTAL_QUESTIONS = len(QUESTIONS)
SKIP_PHRASES    = ["recommend", "just recommend", "skip", "go ahead", "suggest now",
                   "just tell me", "move on", "enough questions", "recommend me now", "recommend me"]

# =========================================================
# DATA
# =========================================================
@st.cache_data
def load_dandori_data():
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "../../database/db.sqlite")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM courses", conn)
    conn.close()
    df = df.rename(columns={
        'file': 'Class ID', 'title': 'Title',
        'instructor': 'Instructor', 'location': 'Location', 'cost': 'Cost'
    })
    if 'Description' not in df.columns:
        df['Description'] = df['Title']
    return df

def get_client():
    return OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

def wants_to_skip(text: str) -> bool:
    return any(p in text.lower() for p in SKIP_PHRASES)

# =========================================================
# ARTHUR SPEAKS
# =========================================================
def arthur_respond(conversation_history: List[Dict], next_question: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": ARTHUR_SYSTEM.format(next_question=next_question)},
            *conversation_history
        ],
        max_tokens=200, temperature=0.85, presence_penalty=0.3, frequency_penalty=0.2
    )
    return response.choices[0].message.content.strip()

# =========================================================
# CRITERIA EXTRACTION
# =========================================================
def extract_criteria(qa_pairs: List[Tuple]) -> Dict:
    transcript = "\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs])
    client = get_client()
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": f"""Extract course preferences. Return ONLY valid JSON:
- energy, social, learning_style, pace
- interests (list 2-3)
- time_available, setting
- avoid (list or null)
- location (city/town/region mentioned)

Interview:
{transcript}"""}],
        max_tokens=300, temperature=0.3
    )
    raw = re.sub(r"```json\s*|\s*```", "", response.choices[0].message.content.strip()).strip()
    try:
        return json.loads(raw)
    except:
        return {"raw_transcript": transcript}

# =========================================================
# RECOMMENDATION
# =========================================================
def recommend_courses(criteria: Dict, df: pd.DataFrame) -> str:
    client = get_client()
    courses_text = "\n".join([
        f"- {r['Title']} | {r.get('Instructor','')} | {r['Location']} | £{r['Cost']} | {r.get('Description','')}"
        for _, r in df.iterrows()
    ])
    system = ARTHUR_RECOMMENDATION_SYSTEM.format(
        criteria=json.dumps(criteria, ensure_ascii=False),
        location=criteria.get("location", "unknown"),
        courses=courses_text
    )
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "Please share your recommendations."}
        ],
        max_tokens=500, temperature=0.7
    )
    return response.choices[0].message.content.strip()

# =========================================================
# PARSE RECOMMENDATIONS
# =========================================================
def parse_recommendations(raw_text: str) -> Tuple[List[str], List[Dict]]:
    lines = raw_text.strip().split("\n")
    intro_lines, courses_map = [], {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m_c = re.match(r"COURSE_(\d):\s*(.+)", line)
        m_w = re.match(r"WHY_(\d):\s*(.+)", line)
        if m_c:
            courses_map.setdefault(m_c.group(1), {})["title_block"] = m_c.group(2)
        elif m_w:
            courses_map.setdefault(m_w.group(1), {})["why"] = m_w.group(2)
        elif not courses_map:
            intro_lines.append(line)
    courses_list = []
    for n in ["1", "2", "3"]:
        if n not in courses_map:
            continue
        parts = [p.strip() for p in courses_map[n].get("title_block", "").split("|")]
        courses_list.append({
            "title":    parts[0] if parts else "—",
            "location": parts[1] if len(parts) > 1 else "",
            "cost":     parts[2] if len(parts) > 2 else "",
            "why":      courses_map[n].get("why", ""),
        })
    return intro_lines, courses_list

# =========================================================
# RENDER RECOMMENDATIONS
# =========================================================
def render_recommendations(raw_text: str):
    intro_lines, courses_list = parse_recommendations(raw_text)
    if intro_lines:
        st.markdown(
            '<div style="background:white;border:1px solid var(--mist);border-radius:4px 16px 16px 16px;'
            'padding:1.1rem 1.4rem;box-shadow:0 2px 12px rgba(0,0,0,0.04);margin-bottom:1.5rem;'
            'font-family:\'Quicksand\',sans-serif;font-size:0.95rem;line-height:1.8;color:#344E41;">'
            + "<br>".join(intro_lines) +
            '</div>',
            unsafe_allow_html=True
        )
    for i, c in enumerate(courses_list):
        col_card, col_btn = st.columns([6, 1], vertical_alignment="center")
        with col_card:
            st.markdown(
                '<div class="course-card">'
                '<div class="title">' + c['title'] + '</div>'
                '<div class="meta">' + c['location'] + ' &nbsp;&middot;&nbsp; ' + c['cost'] + '</div>'
                '<div class="desc">' + c['why'] + '</div>'
                '</div>',
                unsafe_allow_html=True
            )
        with col_btn:
            if st.button("Book →", key=f"book_{i}", use_container_width=True):
                st.session_state.booking_course = c
                st.session_state.booking_step   = "form"
                st.rerun()

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="sanctuary-header">
    <div class="wordmark">THE SCHOOL OF DANDORI</div>
    <div style="text-align:center;margin:0.4rem 0;">
        <iframe src="https://lottie.host/embed/42fb9e10-dbad-4a6f-8eb2-2263a6cdc2b4/xYOZwx81cZ.lottie"
        style="width:600px;height:200px;border:none;"></iframe>
    </div>
    <div class="subtitle">A QUIET SPACE TO DISCOVER YOUR NEXT PRACTICE</div>
</div>
""", unsafe_allow_html=True)

df = load_dandori_data()

# =========================================================
# BOOKING PAGES — short-circuit
# =========================================================
if st.session_state.booking_step == "form":
    c = st.session_state.booking_course
    st.markdown(
        '<div style="background:white;border:1px solid var(--mist);border-radius:20px;'
        'padding:2rem 2.2rem;box-shadow:0 8px 32px rgba(0,0,0,0.06);margin:1rem 0 0;">'
        '<div style="font-family:\'Quicksand\',sans-serif;font-size:1.4rem;font-weight:700;'
        'color:#344E41;margin-bottom:0.2rem;">' + c['title'] + '</div>'
        '<div style="font-size:0.75rem;color:#9A9490;letter-spacing:0.05em;">'
        + c['location'] + ' &nbsp;&middot;&nbsp; ' + c['cost'] +
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="policy-notice" style="margin-top:1rem;">
        <strong>📋 Booking Policy — please read before confirming</strong><br>
        · <strong>Payment must be completed before the course starts.</strong>
          Unpaid bookings will not be admitted on the day.<br>
        · A <strong>cancellation fee applies</strong> for cancellations made less than
          48 hours before the course date.<br>
        · If paying at the counter, please arrive
          <strong>at least 15 minutes early</strong> to complete payment.
    </div>
    """, unsafe_allow_html=True)
    with st.form("booking_form", clear_on_submit=False):
        st.markdown("##### Your details")
        col1, col2 = st.columns(2)
        with col1: first = st.text_input("First name", placeholder="e.g. Selin")
        with col2: last  = st.text_input("Last name",  placeholder="e.g. Yılmaz")
        email = st.text_input("Email address", placeholder="you@example.com")
        col3, col4 = st.columns(2)
        with col3: date         = st.date_input("Preferred date")
        with col4: participants = st.selectbox("Participants", [1, 2, 3, 4, 5])
        notes = st.text_area(
            "Anything Arthur should know before you arrive?",
            placeholder="Dietary needs, accessibility, or just a thought…", height=80
        )
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        cb, cs = st.columns([1, 2])
        with cb: back   = st.form_submit_button("← Back", use_container_width=True)
        with cs: submit = st.form_submit_button("Confirm booking", use_container_width=True, type="primary")

    st.markdown("##### Payment method")
    payment = st.radio(
        "How would you like to pay?",
        ["💳 Pay now (card)", "🏛️ Pay at the counter"],
        key="payment_method",
        help="Payment must be completed before the course starts."
    )
    card_number = card_expiry = card_name = card_cvv = None
    if payment == "💳 Pay now (card)":
        st.markdown("##### Card details")
        cc1, cc2 = st.columns([3, 1])
        with cc1: card_number = st.text_input("Card number", placeholder="1234 5678 9012 3456", max_chars=19)
        with cc2: card_expiry = st.text_input("Expiry", placeholder="MM/YY", max_chars=5)
        cc3, cc4 = st.columns([3, 1])
        with cc3: card_name = st.text_input("Name on card")
        with cc4: card_cvv  = st.text_input("CVV", placeholder="123", max_chars=3, type="password")
    else:
        st.info("You'll pay at the venue. Please arrive 15 minutes early.")

    if back:
        st.session_state.booking_step   = None
        st.session_state.booking_course = None
        st.rerun()
    if submit:
        if not first or not email:
            st.warning("Please fill in your name and email to continue.")
        elif payment == "💳 Pay now (card)" and (not card_number or not card_expiry or not card_cvv):
            st.warning("Please complete your card details.")
        else:
            details = {
                "name": f"{first} {last}".strip(), "email": email,
                "date": str(date), "participants": participants,
                "notes": notes,
                "payment": "Paid by card" if payment == "💳 Pay now (card)" else "Pay at counter",
            }
            st.session_state.booking_step    = "confirmed"
            st.session_state.booking_details = details
            if "booked_courses" not in st.session_state:
                st.session_state.booked_courses = []
            st.session_state.booked_courses.append({
                "course": st.session_state.booking_course, "details": details
            })
            st.rerun()
    st.stop()

if st.session_state.booking_step == "confirmed":

    if not st.session_state.get("balloons_shown", False):
        st.balloons()
        st.session_state.balloons_shown = True

    c  = st.session_state.booking_course
    bd = st.session_state.get("booking_details", {})
    st.markdown(
        '<div style="text-align:center;padding:2.5rem 1rem;">'
        '<div style="font-size:2.5rem;margin-bottom:1rem;">&#127807;</div>'
        '<div style="font-family:\'Quicksand\',sans-serif;font-size:1.9rem;font-weight:700;'
        'color:#344E41;margin-bottom:0.5rem;">You\'re booked in.</div>'
        '<div style="font-size:0.88rem;color:#9A9490;margin-bottom:2rem;">'
        'A confirmation will be sent to <strong>' + bd.get("email", "") + '</strong>'
        '</div>'
        '<div style="background:white;border:1px solid #C8D5C2;border-radius:16px;'
        'padding:1.5rem 1.8rem;max-width:420px;margin:0 auto;text-align:left;'
        'box-shadow:0 4px 20px rgba(0,0,0,0.04);">'
        '<div style="font-family:\'Quicksand\',sans-serif;font-size:1.05rem;font-weight:700;'
        'color:#344E41;margin-bottom:0.3rem;">' + c['title'] + '</div>'
        '<div style="font-size:0.78rem;color:#9A9490;margin-bottom:0.8rem;">'
        + c['location'] + ' &nbsp;&middot;&nbsp; ' + c['cost'] +
        '</div>'
        '<hr style="border:none;border-top:1px solid #E8EFE4;margin:0.6rem 0;">'
        '<div style="font-size:0.84rem;color:#4A4845;line-height:2.1;">'
        '&#128100; &nbsp; ' + bd.get("name", "") + '<br>'
        '&#128197; &nbsp; ' + bd.get("date", "") + '<br>'
        '&#128101; &nbsp; ' + str(bd.get("participants", 1)) + ' participant(s)<br>'
        '&#128179; &nbsp; ' + bd.get("payment", "") +
        '</div>'
        '</div>'
        '<div style="background:#FFF8F0;border:1px solid #E8C99A;border-left:4px solid #D4A853;'
        'border-radius:10px;padding:0.9rem 1.2rem;max-width:420px;margin:1.2rem auto 0;'
        'font-size:0.77rem;color:#7A5C38;line-height:1.9;text-align:left;">'
        '<strong>Reminder:</strong> Payment must be completed before the course starts. '
        'Cancellations within 48 hours are subject to a cancellation fee.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back to recommendations", use_container_width=True):
            st.session_state.booking_step   = None
            st.session_state.booking_course = None
            st.rerun()
    with col_b:
        if st.button("Start over", use_container_width=True):
            booked = st.session_state.get("booked_courses", [])
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.booked_courses = booked
            st.rerun()
    st.stop()

# =========================================================
# PROGRESS INDICATOR
# =========================================================
if st.session_state.criteria is None:
    qi = st.session_state.question_index
    steps_html = '<div class="progress-sidebar">'
    for i, label in enumerate(STEP_LABELS):
        if i < qi:
            cc, ct, lc, lnc = "done", "&#10003;", "", "done"
        elif i == qi:
            cc, ct, lc, lnc = "active", str(i+1), "active", ""
        else:
            cc, ct, lc, lnc = "", str(i+1), "", ""
        steps_html += (
            '<div class="progress-step">'
            '<div class="progress-row">'
            '<div class="progress-circle ' + cc + '">' + ct + '</div>'
            '<span class="progress-label ' + lc + '">' + label + '</span>'
            '</div>'
        )
        if i < len(STEP_LABELS) - 1:
            steps_html += '<div class="progress-line ' + lnc + '"></div>'
        steps_html += '</div>'
    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)

# =========================================================
# CHAT HISTORY
# =========================================================
if st.session_state.chat_history is None:
    opening = f"Hi, I'm Arthur — welcome.\n\nThis is a quiet space. No right answers, no hurry.\n\n*{QUESTIONS[0]}*"
    st.session_state.chat_history = [{"role": "assistant", "content": opening}]
    st.session_state.api_history  = [{"role": "assistant", "content": opening}]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🌿" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

if st.session_state.raw_recommendations and not st.session_state.recommendations_rendered:
    render_recommendations(st.session_state.raw_recommendations)
    st.session_state.recommendations_rendered = True
elif st.session_state.raw_recommendations:
    render_recommendations(st.session_state.raw_recommendations)

# =========================================================
# USER INPUT
# =========================================================
user_input = st.chat_input("Share your thoughts…")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.api_history.append( {"role": "user", "content": user_input})

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    if st.session_state.criteria is None:
        current_q = QUESTIONS[st.session_state.question_index]
        st.session_state.qa_pairs.append((current_q, user_input))
        st.session_state.question_index += 1

        skip_now = wants_to_skip(user_input) or st.session_state.question_index >= TOTAL_QUESTIONS

        if not skip_now:
            next_q    = QUESTIONS[st.session_state.question_index]
            typing_ph = st.empty()
            typing_ph.markdown(
                '<div class="typing-indicator"><span></span><span></span><span></span></div>',
                unsafe_allow_html=True
            )
            time.sleep(1.2)
            arthur_msg = arthur_respond(st.session_state.api_history, next_q)
            typing_ph.empty()
            st.session_state.chat_history.append({"role": "assistant", "content": arthur_msg})
            st.session_state.api_history.append( {"role": "assistant", "content": arthur_msg})
            with st.chat_message("assistant", avatar="🌿"):
                st.markdown(arthur_msg)
        else:
            typing_ph = st.empty()
            typing_ph.markdown(
                '<div class="typing-indicator"><span></span><span></span><span></span></div>',
                unsafe_allow_html=True
            )
            time.sleep(1.5)
            st.session_state.criteria            = extract_criteria(st.session_state.qa_pairs)
            raw_recs                             = recommend_courses(st.session_state.criteria, df)
            st.session_state.raw_recommendations = raw_recs
            typing_ph.empty()
            lines = raw_recs.strip().split("\n")
            intro = " ".join(l.strip() for l in lines
                             if l.strip() and not re.match(r"(COURSE|WHY)_\d", l))
            intro = intro or "Here's what I'd suggest for you…"
            st.session_state.chat_history.append({"role": "assistant", "content": intro})
            st.session_state.api_history.append( {"role": "assistant", "content": intro})
            with st.chat_message("assistant", avatar="🌿"):
                st.markdown(intro)
            render_recommendations(raw_recs)
            st.session_state.recommendations_rendered = True

    st.rerun()  