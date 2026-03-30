import requests
from streamlit_lottie import st_lottie
import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="School of Dandori | Sanctuary", layout="wide", page_icon="🌿")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# --- WELLBEING THEME STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Quicksand', sans-serif;
}

.main {
    background: linear-gradient(180deg, #F0F2F0 0%, #E6EBE0 100%);
}

h1, h2, h3 {
    color: #344E41;
    font-weight: 500;
    letter-spacing: -0.5px;
}

/* Search Section Styling */
.stTextInput > div > div {
    background-color: white;
    border-radius: 12px;
    border: 2px solid #A3B18A;
}

.stTextInput input {
    font-size: 1.1rem;
    padding: 12px;
}

/* Info box styling */
div[data-testid="stMarkdownContainer"] div[data-testid="stMarkdownContainer"] p {
    font-size: 1rem;
}

/* Course Card Containers */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background-color: white;
    padding: 24px;
    border-radius: 16px;
    border: 2px solid rgba(163, 177, 138, 0.3);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover {
    border-color: #A3B18A;
    box-shadow: 0 4px 16px rgba(163, 177, 138, 0.25);
    transform: translateY(-2px);
}

/* Button Styling */
.stButton>button {
    background-color: #A3B18A;
    color: white;
    border-radius: 25px;
    border: none;
    padding: 10px 25px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: #588157;
    border: none;
    color: white;
    transform: translateY(-2px);
}

/* Sidebar refinement */
section[data-testid="stSidebar"] {
    background-color: #F9F6EE;
}

section[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR LOGO ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("Screenshot 2026-03-27 at 16.45.21.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

# --- MOCK FUNCTIONS ---
def create_user_if_not_exists(user_id):
    return

def get_favorites(user_id):
    return []

# --- LOGIN / ENTRANCE ---
if "user_id" not in st.session_state:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("🍃 School of Dandori")
        st.subheader("The philosophy of the school is that we should enjoy our time and look after our wellbeing.")
        st.write("*We offer a range of activities and courses to help you find your flow and connect with others. Please enter a name or ID to access the sanctuary.*")
        user_input = st.text_input("How shall we address you?", placeholder="Enter a name or ID...")
        if st.button("Enter the Sanctuary"):
            if user_input.strip():
                st.session_state.user_id = user_input.strip()
                st.success(f"Welcome home, {user_input}. Take a deep breath.")
                st.rerun()
    with col2:
        st.image("app/Screenshot 2026-03-27 at 16.45.21.png")
    st.stop()

user_id = st.session_state.user_id

# --- LOAD DATA FROM DATABASE ---
import sqlite3

# Connect to the database
conn = sqlite3.connect("../database/db.sqlite")

# Read all courses from the database
df = pd.read_sql_query("SELECT * FROM courses", conn)
conn.close()

# Add the columns that the website UI expects
df = df.rename(columns={
    'file': 'Class ID',
    'title': 'Title',
    'instructor': 'Instructor',
    'location': 'Location',
    'cost': 'Cost'
})

# Add default values for columns we don't have yet
df['Type'] = 'Wellbeing'  # All courses are wellbeing courses
df['Description'] = df['Title'].apply(lambda x: f"A mindful {x.lower()} experience")
df['Skills'] = df.apply(lambda x: ['Mindfulness', 'Creativity', 'Wellbeing'], axis=1)

print(f"📊 Loaded {len(df)} courses from database!")





# --- HEADER ---
col1, col2 = st.columns([1, 1])
with col1:
    st.title("🌿 School of Dandori")
    st.write(f"Hello, **{user_id}**. Find your next course:")
with col2:
    st.markdown('<iframe src="https://lottie.host/embed/42fb9e10-dbad-4a6f-8eb2-2263a6cdc2b4/xYOZwx81cZ.lottie" style="width:100%;height:300px;border:none;background:transparent;" allowfullscreen></iframe>', unsafe_allow_html=True)

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("Refine Your Intent")
    location = st.selectbox("Where would you like to go?", ["Everywhere"] + sorted(df["Location"].unique().tolist()))
    course_type = st.selectbox("Style of Practice", ["All Styles"] + sorted(df["Type"].unique().tolist()))
    max_cost = st.slider("Investment Range (£)", 0, 200, 200)
    
    all_skills = sorted({skill for sublist in df["Skills"] for skill in sublist})
    selected_skills = st.multiselect("Inner qualities to nurture:", all_skills)

# --- FILTERING LOGIC ---
filtered_df = df.copy()
if location != "Everywhere":
    filtered_df = filtered_df[filtered_df["Location"] == location]
if course_type != "All Styles":
    filtered_df = filtered_df[filtered_df["Type"] == course_type]
filtered_df = filtered_df[filtered_df["Cost"] <= max_cost]

if selected_skills:
    filtered_df = filtered_df[filtered_df["Skills"].apply(lambda s: any(x in s for x in selected_skills))]

# --- CONTENT AREA ---
st.markdown("### 🔍 Search for an Experience")
search_query = st.text_input("", placeholder="e.g., 'pottery', 'yoga', 'weaving'", label_visibility="collapsed")

if search_query:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]

# Show helpful tip right under search bar
if location == "Everywhere" and course_type == "All Styles" and not search_query:
    st.info("💡 Showing featured courses. Use filters on the left or search above to explore more.")

st.markdown("---")

# --- DISPLAY LOGIC ---
show_featured = (
    location == "Everywhere" and 
    course_type == "All Styles" and 
    max_cost == 200 and 
    not selected_skills and 
    not search_query
)

# Determine which courses to show
if show_featured and not filtered_df.empty:
    st.markdown("## ✨ Featured Experiences")
    st.markdown("<br>", unsafe_allow_shtml=True)
    display_df = filtered_df.sample(n=min(5, len(filtered_df)))
else:
    display_df = filtered_df

# --- COURSE CARD DISPLAY ---
if display_df.empty:
    st.info("The path is quiet today. Perhaps try a different search? 🌿")
else:
    # Display in 2-column layout
    for i in range(0, len(display_df), 2):
        cols = st.columns(2, gap="medium")
        
        for col_idx in range(2):
            if i + col_idx < len(display_df):
                row = display_df.iloc[i + col_idx]
                
                with cols[col_idx]:
                    # Card container with border
                    with st.container(border=True):
                        # Title
                        st.markdown(f"### {row['Title']}")
                        
                        # Instructor and location
                        st.markdown(f"<p style='text-align: center; color: #6B705C; font-style: italic;'>👤 {row['Instructor']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align: center; color: #6B705C; font-style: italic;'>📍 {row['Location']}</p>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Description
                        st.write(row['Description'][:120] + "...")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Skills
                        skills_text = " • ".join(row['Skills'][:3])
                        st.markdown(f"<p style='text-align: center; background: #F9F6EE; padding: 10px; border-radius: 8px; color: #588157;'><b>Focus:</b> {skills_text}</p>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Price (centered)
                        st.markdown(f"<h2 style='text-align: center; color: #A3B18A; margin: 10px 0;'>£{row['Cost']}</h2>", unsafe_allow_html=True)
                        
                        # Reserve button
                        if st.button("Reserve Your Spot", key=row['Class ID'], use_container_width=True):
                            st.balloons()
                            st.success(f"✨ Your journey to {row['Title']} has been noted!")
        
        st.markdown("<br>", unsafe_allow_html=True)

        
# --- Contact ---

with st.container():
    st.write("---")
    st.header("Get in Touch with Arthur!")
    contact_form= """
    <form action="https://formsubmit.co/arthur@email.com" method="POST">
     <input type="hidden" name"_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here" required></textarea>
     <button type="submit">Send</button>
</form>
"""
left_column, right_column = st.columns([2,1])
with left_column:
    st.markdown(contact_form, unsafe_allow_html=True)
with right_column:
    st.markdown('<iframe src="https://lottie.host/embed/51d9c5d3-d3a4-4c13-9569-afef8299a530/smBgQyQ8E4.lottie"></iframe>', unsafe_allow_html=True)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("app/style/style.css")

