import requests
from streamlit_lottie import st_lottie
import streamlit as st
import pandas as pd
import sqlite3
import os
import json

SAVE_FILE = "bookings.json"

def load_bookings():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return []

def save_bookings(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

LOG_FILE = "booking_log.json"

from datetime import datetime

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_booking(course, user):
    log = load_log()

    # ✅ handle both old + new formats
    if "course" in course:
        c = course["course"]
    else:
        c = course

    log_entry = {
        "user": user,
        "title": c["title"],
        "location": c["location"],
        "cost": c["cost"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    log.append(log_entry)
    save_log(log)
# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="School of Dandori",
    layout="wide",
    page_icon="🍃",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# BRAND-ALIGNED PROFESSIONAL STYLING
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600&display=swap');

* {
    font-family: 'Quicksand', sans-serif;
}

h1, h2, h3 {
    font-family: 'Quicksand', sans-serif;
    color: #344E41;
    font-weight: 500;
}

/* Main Background - Warm cream gradient */
.main {
    background: linear-gradient(180deg, #F9F6EE 0%, #FBF9F3 100%);
}
/* Remove Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar Styling - Brand cream */
section[data-testid="stSidebar"] {
    background: #F9F6EE;
    border-right: 1px solid rgba(163, 177, 138, 0.2);
    padding: 1.5rem 1rem;
}

section[data-testid="stSidebar"] h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #344E41;
    margin-bottom: 1.5rem;
    letter-spacing: 0.3px;
}

/* Input Fields - Clean with sage accents */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div {
    border-radius: 10px;
    border: 1.5px solid rgba(163, 177, 138, 0.3);
    background: white;
    transition: border-color 0.2s ease;
}

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover,
.stTextInput > div > div:hover {
    border-color: #A3B18A;
}

.stSelectbox label,
.stMultiSelect label,
.stSlider label {
    font-size: 0.88rem;
    font-weight: 500;
    color: #344E41;
    margin-bottom: 0.5rem;
}

/* Slider styling */
.stSlider > div > div > div {
    background: #A3B18A;
}

/* Search Bar - Clean professional style */
.stTextInput {
    margin-bottom: 1.5rem;
}

.stTextInput > div > div {
    background: white;
    border-radius: 12px;
    border: 2px solid rgba(163, 177, 138, 0.3);
    box-shadow: 0 2px 8px rgba(163, 177, 138, 0.08);
    transition: all 0.2s ease;
}

.stTextInput > div > div:hover {
    border-color: #A3B18A;
    box-shadow: 0 4px 12px rgba(163, 177, 138, 0.12);
}

.stTextInput > div > div:focus-within {
    border-color: #A3B18A;
    box-shadow: 0 4px 16px rgba(163, 177, 138, 0.2);
}

.stTextInput input {
    font-size: 1rem;
    padding: 1rem 1.25rem;
    color: #344E41;
}

.stTextInput input::placeholder {
    color: #A3B18A;
    opacity: 0.7;
}

/* Info Banner - Brand colors */
div[data-testid="stMarkdown"] .element-container div.stAlert {
    background: rgba(163, 177, 138, 0.08);
    border-left: 4px solid #A3B18A;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    color: #344E41;
}

/* Course Cards - White with sage accents */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border: 2px solid rgba(163, 177, 138, 0.25) !important;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(52, 78, 65, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
}

div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    border-color: #A3B18A !important;
    box-shadow: 0 8px 24px rgba(163, 177, 138, 0.15);
    transform: translateY(-6px);
}

/* Buttons - Sage green brand color */
.stButton > button {
    background: #A3B18A;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.85rem 2rem;
    font-weight: 500;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    width: 100%;
    letter-spacing: 0.2px;
}

.stButton > button:hover {
    background: #588157;
    box-shadow: 0 6px 16px rgba(163, 177, 138, 0.35);
    transform: translateY(-2px);
}

/* Typography */
.course-title {
    font-family: 'Quicksand', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #344E41;
    margin-bottom: 0.75rem;
    line-height: 1.4;
}

.course-meta {
    font-size: 0.9rem;
    color: #6B705C;
    margin-bottom: 1rem;
    font-weight: 400;
}

.course-description {
    font-size: 0.95rem;
    line-height: 1.7;
    color: #344E41;
    margin-bottom: 1.5rem;
    font-weight: 300;
}

.course-skills {
    background: rgba(163, 177, 138, 0.08);
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #588157;
    margin-bottom: 1.5rem;
    border-left: 3px solid #A3B18A;
    font-weight: 500;
}

.course-price {
    font-family: 'Quicksand', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    color: #A3B18A;
    margin-bottom: 1rem;
}

/* Header */
.main-header {
    margin-bottom: 2rem;
}

.main-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    color: #344E41;
    font-weight: 500;
}

.main-header p {
    font-size: 1.1rem;
    color: #6B705C;
    font-weight: 300;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid rgba(163, 177, 138, 0.2);
    margin: 2rem 0;
}

/* Section Headers */
.section-header {
    font-family: 'Quicksand', sans-serif;
    font-size: 1.8rem;
    color: #344E41;
    margin: 2rem 0 1.5rem 0;
    font-weight: 500;
}

/* Success message styling */
.stSuccess {
    background: rgba(163, 177, 138, 0.1);
    border-left: 4px solid #A3B18A;
    color: #344E41;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════
if "user_id" not in st.session_state:
    # We use the middle column (col2) for our content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        sub_col1, sub_col2, sub_col3 = st.columns([1, 2, 1])
        with sub_col2:
            st.image("app/Screenshot 2026-03-27 at 16.45.21.png", width=220)
        
        # --- HEADER & TEXT ---
        st.markdown("<h1 style='text-align: center; font-family: Quicksand; color: #344E41;'>School of Dandori</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B705C; font-size: 1.1rem;'>The philosophy of the school is that we should enjoy our time and look after our wellbeing.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- INPUT & BUTTON ---
        user_input = st.text_input("How shall we address you?", placeholder="Enter your name...", label_visibility="collapsed")
        
        if st.button("Enter the Sanctuary", use_container_width=True):
            if user_input.strip():
                st.session_state.user_id = user_input.strip()
                st.success(f"Welcome home, {user_input}. Take a deep breath.")
                st.rerun()
    st.stop()

user_id = st.session_state.user_id

# ═══════════════════════════════════════════════════════════════════
# LOAD DATA FROM DATABASE
# ═══════════════════════════════════════════════════════════════════
@st.cache_data
def load_courses():
    db_path = os.path.join(os.path.dirname(__file__), "../database/db.sqlite")
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
    
    df['Type'] = 'Wellbeing'
    df['Description'] = df['Title'].apply(lambda x: f"A mindful journey into {x.lower()}. Reconnect with your creative spirit.")
    df['Skills'] = df.apply(lambda x: ['Mindfulness', 'Creativity', 'Presence'], axis=1)
    
    return df

df = load_courses()


# ═══════════════════════════════════════════════════════════════════
# SESSION STATE (WITH PERSISTENCE)
# ═══════════════════════════════════════════════════════════════════
if "booked_courses" not in st.session_state:
    st.session_state.booked_courses = load_bookings()

if "panel_open" not in st.session_state:
    st.session_state.panel_open = False


def add_course(course, paid=False):
    titles = [
        c["course"]["title"] if "course" in c else c["title"]
        for c in st.session_state.booked_courses
    ]

    new_title = course["course"]["title"] if "course" in course else course["title"]

    if new_title not in titles:
        course_entry = course.copy()
        course_entry["paid"] = paid
        st.session_state.booked_courses.append(course)
        save_bookings(st.session_state.booked_courses)


def remove_course(index):
    st.session_state.booked_courses.pop(index)
    save_bookings(st.session_state.booked_courses)

if "booking_step" not in st.session_state:
    st.session_state.booking_step = None

if "booking_course" not in st.session_state:
    st.session_state.booking_course = None

if "booking_details" not in st.session_state:
    st.session_state.booking_details = {}

# =========================================================
# BOOKING FLOW (same as Questionnaire)
# =========================================================

if st.session_state.booking_step == "form":
    c = st.session_state.booking_course

    st.markdown(f"## Booking: {c['title']}")
    st.markdown(f"{c['location']} · {c['cost']}")

    # ✅ PAYMENT
    st.markdown("##### Payment method")
    payment = st.radio(
        "How would you like to pay?",
        ["💳 Pay now (card)", "🏛️ Pay at the counter"],
        help="Payment must be completed before the course starts."
    )

    with st.form("booking_form"):
        first = st.text_input("First name")
        email = st.text_input("Email")

        date = st.date_input("Preferred date")
        participants = st.selectbox("Participants", [1,2,3,4])


        card_number = card_expiry = card_name = card_cvv = None

        if payment == "💳 Pay now (card)":
            st.markdown("##### Card details")

            cc1, cc2 = st.columns([3, 1])
            with cc1:
                card_number = st.text_input("Card number", placeholder="1234 5678 9012 3456", max_chars=19)
            with cc2:
                card_expiry = st.text_input("Expiry", placeholder="MM/YY", max_chars=5)

            cc3, cc4 = st.columns([3, 1])
            with cc3:
                card_name = st.text_input("Name on card")
            with cc4:
                card_cvv = st.text_input("CVV", placeholder="123", max_chars=3, type="password")

        else:
            st.info("You'll pay at the venue. Please arrive 15 minutes early.")

        submit = st.form_submit_button("Confirm booking")
        back = st.form_submit_button("← Back")

    # ⬇️ FORM DIŞI (çok önemli)
    if back:
        st.session_state.booking_step = None
        st.rerun()

    if submit:
        if not first or not email:
            st.warning("Please fill in your name and email to continue.")

        elif payment == "💳 Pay now (card)" and (
            not card_number or not card_expiry or not card_cvv or not card_name
        ):
            st.warning("Please complete your card details.")

        else:
            st.session_state.booking_details = {
                "name": first,
                "email": email,
                "date": str(date),
                "participants": participants,
                "payment": "Paid by card" if payment == "💳 Pay now (card)" else "Pay at counter"
            }

            is_paid = payment == "💳 Pay now (card)"

            updated = False
            for b in st.session_state.booked_courses:
                booked_course = b["course"] if "course" in b else b
                if booked_course["title"] == c["title"]:
                    b["details"] = st.session_state.booking_details
                    b["paid"] = is_paid
                    updated = True
                    break

            if not updated:
                st.session_state.booked_courses.append({
                    "course": c,
                    "details": st.session_state.booking_details,
                    "paid": is_paid
                })

            save_bookings(st.session_state.booked_courses)
            log_booking({"course": c, "details": st.session_state.booking_details, "paid": is_paid}, st.session_state.user_id)

            st.session_state.booking_step = "confirmed"
            st.session_state.panel_open = True
            st.balloons()
            st.success("✨ Your booking has been confirmed!")
            st.rerun()

    st.stop()

# =========================================================
# CONFIRMED BOOKING DISPLAY
# =========================================================
if st.session_state.booking_step == "confirmed":
    c = st.session_state.booking_course
    bd = st.session_state.booking_details

    st.balloons()
    st.success("✨ Your booking has been confirmed!")

    st.markdown(f"""
    ### {c['title']}
    {c['location']} · {c['cost']}

    👤 {bd['name']}  
    📅 {bd['date']}  
    👥 {bd['participants']} people  
    💳 {bd['payment']}
    """)

    if st.button("← Back to courses"):
        st.session_state.booking_step = None
        st.session_state.booking_course = None
        st.rerun()

    st.stop()
# ═══════════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
.bookings-panel {{
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    width: 320px;
    background: white;
    border-left: 1px solid rgba(163, 177, 138, 0.3);
    padding: 80px 20px 20px 20px;
    z-index: 9999;
}}

.booking-card {{
    background: #F9F6EE;
    border: 1px solid #E6EBE0;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
}}

.remove-btn {{
    background: none;
    border: none;
    color: #BC6C25;
    font-size: 0.8rem;
    cursor: pointer;
    float: right;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - FILTERS
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.image("app/Screenshot 2026-03-27 at 16.45.21.png", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Filters")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Location filter
    location = st.selectbox(
        "Location",
        ["All Locations"] + sorted(df["Location"].unique().tolist())
    )
    
    # Type filter
    course_type = st.selectbox(
        "Practice Style",
        ["All Styles"] + sorted(df["Type"].unique().tolist())
    )
    
    # Price filter
    max_cost = st.slider(
        "Maximum Investment (£)",
        min_value=0,
        max_value=200,
        value=200,
        step=5
    )
    
    # Skills filter
    all_skills = sorted({skill for sublist in df["Skills"] for skill in sublist})
    selected_skills = st.multiselect(
        "Inner Qualities",
        all_skills
    )
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button(f"🛒 My Courses ({len(st.session_state.booked_courses)})"):
        st.session_state.panel_open = not st.session_state.panel_open
        st.rerun()
    st.markdown("---")
    st.caption(f"Signed in as **{user_id}**")


# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>🍃 Welcome, {user_id}</h1>
        
    </div>
    """, unsafe_allow_html=True)
    if st.button("💬 Ask our Chatbot"):
        st.switch_page("pages/1_Questionnaire.py")

with col2:
    st.markdown("""
    <a href="/Chatbot" target="_self" style="text-decoration: none;">
        <iframe src="https://lottie.host/embed/42fb9e10-dbad-4a6f-8eb2-2263a6cdc2b4/xYOZwx81cZ.lottie"
        style="width:100%;height:300px;border:none;background:transparent;cursor:pointer;"
        allowfullscreen></iframe>
    </a>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PANEL CONTENT
# ═══════════════════════════════════════════════════════════════════
if st.session_state.panel_open:
    st.markdown("### 🛒 My Courses")

    if not st.session_state.booked_courses:
        st.markdown("<p style='color:#A3B18A;'>No paths chosen yet.</p>", unsafe_allow_html=True)

    for i, b in enumerate(st.session_state.booked_courses):
        course_data = b["course"] if "course" in b else b
        c = b["course"] if "course" in b else b
        paid = b.get("paid", False)
        with st.container():
            col1, col2 = st.columns([5, 2])

            # LEFT: course info
            with col1:
                st.markdown(f"""
                <div class="booking-card">
                    <div style="color:#344E41;font-weight:600;">{course_data['title']}</div>
                    <div style="color:#6B705C;font-size:0.8rem;">
                        📍 {course_data['location']} · <b>{course_data['cost']}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # RIGHT: buttons
            with col2:
                btn1, btn2 = st.columns(2)

                # 💳 PAY NOW
                with btn1:
                    if st.button("💳", key=f"pay_{i}_{c['title']}"):
                        st.session_state.booking_course = c
                        st.session_state.booking_step = "form"
                        st.rerun()
                    else:
                        st.button("Paid ✅", key=f"paid_{i}_{c['title']}", disabled=True)

                # ❌ REMOVE
                with btn2:
                    if st.button("❌", key=f"remove_{i}_{c['title']}"):
                        remove_course(i)
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# SEARCH SECTION
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 🔍 Find Your Experience")
search_query = st.text_input(
    "Search",
    placeholder="Try 'pottery', 'yoga', 'Scottish Highlands', or 'mindfulness'...",
    label_visibility="collapsed"
)

# ═══════════════════════════════════════════════════════════════════
# FILTERING LOGIC
# ═══════════════════════════════════════════════════════════════════
filtered_df = df.copy()

if location != "All Locations":
    filtered_df = filtered_df[filtered_df["Location"] == location]
    
if course_type != "All Styles":
    filtered_df = filtered_df[filtered_df["Type"] == course_type]
    
filtered_df = filtered_df[filtered_df["Cost"] <= max_cost]

if selected_skills:
    filtered_df = filtered_df[filtered_df["Skills"].apply(lambda s: any(x in s for x in selected_skills))]

if search_query:
    filtered_df = filtered_df[filtered_df.apply(
        lambda row: search_query.lower() in str(row).lower(), axis=1
    )]

# ═══════════════════════════════════════════════════════════════════
# DISPLAY LOGIC
# ═══════════════════════════════════════════════════════════════════
show_featured = (
    location == "All Locations" and 
    course_type == "All Styles" and 
    max_cost == 200 and 
    not selected_skills and 
    not search_query
)

if show_featured:
    st.info("💡 Showing featured courses. Use the filters or search to explore our full collection.")
    st.markdown('<p class="section-header">Featured Experiences</p>', unsafe_allow_html=True)
    display_df = filtered_df.sample(n=min(6, len(filtered_df)), random_state=42)
else:
    if not filtered_df.empty:
        st.success(f"✓ Found {len(filtered_df)} course{'s' if len(filtered_df) != 1 else ''} matching your criteria")
    display_df = filtered_df

# ═══════════════════════════════════════════════════════════════════
# COURSE DISPLAY
# ═══════════════════════════════════════════════════════════════════
def get_booking_status(course):
    """
    Returns:
        None       -> not booked
        'unpaid'   -> booked but not paid
        'paid'     -> booked and paid
    """
    for b in st.session_state.booked_courses:
        c = b["course"] if "course" in b else b
        if c["title"] == course["Title"]:
            return 'paid' if b.get("paid", False) else 'unpaid'
    return None


if display_df.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("🌿 No courses match your current filters. Try adjusting your search criteria.")
else:
    # Display in 3-column grid
    for i in range(0, len(display_df), 3):
        cols = st.columns(3, gap="large")
        
        for col_idx in range(3):
            if i + col_idx < len(display_df):
                row = display_df.iloc[i + col_idx]
                status = get_booking_status(row)  # None / 'unpaid' / 'paid'

                with cols[col_idx]:
                    with st.container(border=True):
                        # Title with tick if paid
                        tick = " ✅" if status == "paid" else ""
                        st.markdown(f'<p class="course-title">{row["Title"]}{tick}</p>', unsafe_allow_html=True)
                        
                        # Meta info
                        st.markdown(f'<p class="course-meta">👤 {row["Instructor"]}<br>📍 {row["Location"]}</p>', unsafe_allow_html=True)
                        
                        # Description
                        st.markdown(f'<p class="course-description">{row["Description"]}</p>', unsafe_allow_html=True)
                        
                        # Skills
                        skills_text = " • ".join(row["Skills"][:3])
                        st.markdown(f'<div class="course-skills">Focus: {skills_text}</div>', unsafe_allow_html=True)
                        
                        # Price
                        st.markdown(f'<p class="course-price">£{row["Cost"]}</p>', unsafe_allow_html=True)
                        
                        # Buttons
                        if status == 'paid':
                            st.button("Paid ✅", key=f"paid_{row['Class ID']}", disabled=True, use_container_width=True)
                        elif status == 'unpaid':
                            if st.button("💳 Pay now", key=f"pay_{row['Class ID']}", use_container_width=True):
                                st.session_state.booking_course = {
                                    "title": row["Title"],
                                    "location": row["Location"],
                                    "cost": f"£{row['Cost']}"
                                }
                                st.session_state.booking_step = "form"
                                st.rerun()
                        else:  # Not booked yet
                            if st.button("Reserve Your Spot", key=row["Class ID"], use_container_width=True):
                                st.session_state.booking_course = {
                                    "title": row["Title"],
                                    "location": row["Location"],
                                    "cost": f"£{row['Cost']}"
                                }
                                st.session_state.booking_step = "form"
                                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# FOOTER / CONTACT
# ═══════════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<p class="section-header">Get in Touch</p>', unsafe_allow_html=True)
    st.markdown("Have questions? We're here to help you find the perfect course.")
    
    contact_form = """
    <form action="https://formsubmit.co/arthur@email.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message" required></textarea>
        <button type="submit">Send Message</button>
    </form>
    """
    st.markdown(contact_form, unsafe_allow_html=True)

with col2:
    st.markdown('<iframe src="https://lottie.host/embed/51d9c5d3-d3a4-4c13-9569-afef8299a530/smBgQyQ8E4.lottie" style="width:100%;height:300px;border:none;"></iframe>', unsafe_allow_html=True)

# Load custom CSS for contact form
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

css_path = os.path.join(os.path.dirname(__file__), "style/style.css")
local_css(css_path)
