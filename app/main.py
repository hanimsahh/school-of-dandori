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
# Using a palette of Sage (#A3B18A), Cream (#F9F6EE), and Earth (#344E41)
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

/* Softening the Cards */
.stMarkdown div[data-styled-content="true"] > div {
    background-color: rgba(255, 255, 255, 0.7);
    padding: 24px;
    border-radius: 20px;
    border: 1px solid rgba(163, 177, 138, 0.2);
    box-shadow: 0 10px 30px rgba(0,0,0,0.03);
    margin-bottom: 20px;
    transition: transform 0.3s ease;
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
</style>
""", unsafe_allow_html=True)

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

# --- MOCK DATA ---
data = [
    {
        "Class ID": "CLASS_1893",
        "Title": "Enchanted Tartan Weaving",
        "Instructor": "Professor Plaid McLoom",
        "Location": "Scottish Highlands",
        "Cost": 85,
        "Type": "Craft",
        "Description": "Find your rhythm at the loom. A meditative practice connecting thread, history, and heart.",
        "Skills": ["Mindfulness", "Patience", "Artistry"]
    },
    {
        "Class ID": "CLASS_2041",
        "Title": "The Art of Slow Pottery",
        "Instructor": "Ada Clayworth",
        "Location": "Leeds Studio",
        "Cost": 120,
        "Type": "Pottery",
        "Description": "Feel the earth between your fingers. A weekend dedicated to the tactile joy of creation.",
        "Skills": ["Focus", "Presence", "Tactile Healing"]
    }
]
df = pd.DataFrame(data)

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
search_query = st.text_input("🔍 Search for an activity...", placeholder="e.g., 'quiet', 'weaving', 'nature'")

if search_query:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]

st.divider()

if filtered_df.empty:
    st.info("The path is quiet today. Perhaps try a different search? 🌿")
else:
    for _, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div style="margin-bottom: 25px;">
                <h2 style="margin-bottom: 5px;">{row['Title']}</h2>
                <p style="color: #6B705C; font-style: italic;">Guided by {row['Instructor']} • {row['Location']}</p>
                <p>{row['Description']}</p>
                <p style="font-size: 0.9em; color: #344E41;"><b>Focusing on:</b> {", ".join(row['Skills'])}</p>
                <h4 style="color: #A3B18A;">£{row['Cost']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Reserve a Spot: {row['Title']}", key=row['Class ID']):
                st.balloons()
                st.success("Your journey has been noted. We'll see you there. ✨")

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

