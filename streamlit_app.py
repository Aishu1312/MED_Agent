import streamlit as st
from groq import Groq
from gtts import gTTS
import urllib.parse
from PIL import Image
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MedAgent AI", page_icon="🩺", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
}
.big-title {
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#00E5FF;
}
.sub-title {
    text-align:center;
    color:#CBD5E1;
}
.poll-box {
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API ----------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)
LLAMA_MODEL = "llama-3.1-8b-instant"

# ---------------- LANGUAGES ----------------
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
    "Urdu": "ur"
}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    location = st.text_input("📍 Enter City")

# ---------------- HEADER ----------------
st.markdown('<div class="big-title">🩺 MedAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Smart AI Healthcare Assistant</div>', unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def generate_response(symptom, answers, description):
    prompt = f"""
User symptom: {symptom}
Poll answers: {answers}
Extra description: {description}

Provide:
1. Possible cause
2. Precautions/measures
3. Whether doctor consultation is needed
4. Emergency warning signs
"""
    completion = client.chat.completions.create(
        model=LLAMA_MODEL,
        messages=[{"role":"user","content":prompt}]
    )
    return completion.choices[0].message.content

def speak(text):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("response.mp3")
    audio_file = open("response.mp3","rb")
    st.audio(audio_file.read())

# ---------------- SESSION ----------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["💬 AI Doctor", "📍 Nearby Doctors", "🚑 Emergency"])

# ---------------- TAB 1 ----------------
with tab1:
    symptom = st.text_input("Enter your symptom/problem")

    if symptom:
        questions = [
            ("What type of pain are you experiencing?", 
             ["Sharp/Stabbing", "Dull/Aching", "Burning", "Other"]),
            ("How long have you had this?", 
             ["Few minutes", "Hours", "1 day", "More than 1 day"]),
            ("Severity level?", 
             ["Mild", "Moderate", "Severe"])
        ]

        if st.session_state.step < len(questions):
            q, opts = questions[st.session_state.step]
            st.markdown(f"### {q}")
            choice = st.radio("Select one", opts, key=st.session_state.step)

            if st.button("Next"):
                st.session_state.answers[q] = choice
                st.session_state.step += 1
                st.rerun()

        else:
            description = st.text_area("📝 Describe more about your disease/problem")

            if st.button("Get Advice"):
                with st.spinner("Analyzing..."):
                    response = generate_response(symptom, st.session_state.answers, description)
                    st.success("AI Medical Advice")
                    st.write(response)
                    speak(response)

# ---------------- TAB 2 ----------------
with tab2:
    if st.button("Search Doctors"):
        if location:
            query = urllib.parse.quote(f"doctor near {location}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(f"[🔍 Open Google Maps]({maps_url})")

# ---------------- TAB 3 ----------------
with tab3:
    st.write("📞 Ambulance: 108")
    st.write("📞 Emergency: 112")
    st.write("📞 Women Helpline: 1091")
    st.write("📞 Child Helpline: 1098")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 MedAgent AI | Powered by Groq")
