import requests
from streamlit_lottie import st_lottie
import streamlit as st
import pandas as pd
import sqlite3

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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("Screenshot 2026-03-27 at 16.45.21.png", width=220)
        st.markdown("<h1 style='text-align: center; font-family: Quicksand; color: #344E41;'>School of Dandori</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B705C; font-size: 1.1rem;'>The philosophy of the school is that we should enjoy our time and look after our wellbeing.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
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
    conn = sqlite3.connect("../database/db.sqlite")
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
# SIDEBAR - FILTERS
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.image("Screenshot 2026-03-27 at 16.45.21.png", use_container_width=True)
    
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
    st.caption(f"Signed in as **{user_id}**")

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>🍃 Welcome, {user_id}</h1>
        
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<iframe src="https://lottie.host/embed/42fb9e10-dbad-4a6f-8eb2-2263a6cdc2b4/xYOZwx81cZ.lottie" style="width:100%;height:200px;border:none;background:transparent;" allowfullscreen></iframe>', unsafe_allow_html=True)

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
                
                with cols[col_idx]:
                    with st.container(border=True):
                        # Title
                        st.markdown(f'<p class="course-title">{row["Title"]}</p>', unsafe_allow_html=True)
                        
                        # Meta info
                        st.markdown(f'<p class="course-meta">👤 {row["Instructor"]}<br>📍 {row["Location"]}</p>', unsafe_allow_html=True)
                        
                        # Description
                        st.markdown(f'<p class="course-description">{row["Description"]}</p>', unsafe_allow_html=True)
                        
                        # Skills
                        skills_text = " • ".join(row["Skills"][:3])
                        st.markdown(f'<div class="course-skills">Focus: {skills_text}</div>', unsafe_allow_html=True)
                        
                        # Price
                        st.markdown(f'<p class="course-price">£{row["Cost"]}</p>', unsafe_allow_html=True)
                        
                        # Button
                        if st.button("Reserve Your Spot", key=row["Class ID"], use_container_width=True):
                            st.balloons()
                            st.success("✨ Booking confirmed! We look forward to seeing you.")
        
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

local_css("style/style.css")