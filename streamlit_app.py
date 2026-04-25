import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="MedAgent AI",
    page_icon="🩺",
    layout="wide"
)

# ----------------------------
# CUSTOM CSS
# ----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color: white;
}
.stTextInput>div>div>input, .stTextArea textarea {
    border-radius: 12px;
}
.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #00E5FF;
    text-align:center;
}
.sub-title {
    text-align:center;
    font-size:18px;
    color:#cbd5e1;
}
.card {
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    box-shadow:0 0 15px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# API KEY
# ----------------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("API Key missing")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

LLAMA_MODEL = "llama-3.3-70b-versatile"

# ----------------------------
# LANGUAGES
# ----------------------------
languages = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Odia": "or",
    "Assamese": "as",
    "Urdu": "ur",
    "Konkani": "kok",
    "Manipuri": "mni",
    "Bodo": "brx",
    "Dogri": "doi",
    "Maithili": "mai",
    "Santali": "sat",
    "Kashmiri": "ks",
    "Sindhi": "sd",
    "Nepali": "ne",
    "Sanskrit": "sa",
    "Tulu": "tcy",
    "Bhili": "bhb",
    "Rajasthani": "raj",
    "Bhojpuri": "bho"
}

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=100)
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    user_location = st.text_input("📍 Enter City / Location")
    st.markdown("---")
    st.info("MedAgent AI helps with general health guidance.")

# ----------------------------
# FUNCTION
# ----------------------------
def generate_response(prompt):
    try:
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI medical assistant. Give safe and professional medical guidance only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# ----------------------------
# HEADER
# ----------------------------
st.markdown('<div class="big-title">🩺 MedAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Smart AI Healthcare Assistant</div>', unsafe_allow_html=True)

# ----------------------------
# TABS
# ----------------------------
tab1, tab2, tab3 = st.tabs(["💬 AI Doctor", "📍 Nearby Doctors", "🚑 Emergency"])

# ----------------------------
# TAB 1
# ----------------------------
with tab1:
    st.markdown("### Describe your symptoms")
    query = st.text_area("Enter your health issue")

    uploaded_file = st.file_uploader("Upload image/report", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)

    if st.button("Get AI Advice"):
        if query:
            with st.spinner("Analyzing symptoms..."):
                response = generate_response(query)
                st.success("AI Medical Advice")
                st.write(response)

# ----------------------------
# TAB 2
# ----------------------------
with tab2:
    st.markdown("### Find Nearby Doctors")
    if st.button("Search Doctors"):
        if user_location:
            query = urllib.parse.quote(f"doctor near {user_location}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(f"[🔍 Open Google Maps]({maps_url})")
        else:
            st.warning("Please enter your location in sidebar.")

# ----------------------------
# TAB 3
# ----------------------------
with tab3:
    st.markdown("## 🚑 Emergency Contacts")
    st.write("📞 Ambulance: 108")
    st.write("📞 Emergency: 112")
    st.write("📞 Women Helpline: 1091")
    st.write("📞 Child Helpline: 1098")

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.caption("© 2026 MedAgent AI | Powered by Groq")
