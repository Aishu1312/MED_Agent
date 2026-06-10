import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MedAgent AI", page_icon="🩺", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
}
.big-title {
    font-size:42px;
    font-weight:bold;
    text-align:center;
    color:#00E5FF;
}
.sub-title {
    text-align:center;
    color:#CBD5E1;
}
.stButton>button {
    border-radius:12px;
    width:100%;
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
    "Malayalam": "ml"
}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    user_location = st.text_input("📍 Enter City / Location")

# ---------------- HEADER ----------------
st.markdown('<div class="big-title">🩺 MedAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Smart AI Healthcare Assistant</div>', unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def generate_response(prompt):
    completion = client.chat.completions.create(
        model=LLAMA_MODEL,
        messages=[
            {"role": "system", "content": "You are an AI medical assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def text_to_speech(text):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# ---------------- SESSION STATE ----------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["💬 AI Doctor", "📍 Nearby Doctors", "🚑 Emergency"])

# ---------------- TAB 1 ----------------
with tab1:
    st.markdown("### Describe your symptoms")

    # MIC
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key="recorder"
    )

    if audio:
        st.success("Voice recorded successfully!")
        st.audio(audio["bytes"])

    # TEXT INPUT
    query = st.text_area("Enter your symptoms")

    # FILE UPLOAD
    uploaded_file = st.file_uploader("Upload image/report", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file and uploaded_file.type.startswith("image"):
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

    # POLL QUESTIONS
    questions = [
        {
            "q": "What is the severity of your pain?",
            "options": ["1-3 Mild", "4-6 Moderate", "7-10 Severe", "Not sure"]
        },
        {
            "q": "How long have you had these symptoms?",
            "options": ["Few minutes", "Few hours", "1 day", "Several days"]
        },
        {
            "q": "Do you have fever?",
            "options": ["Yes", "No", "Not sure"]
        }
    ]

    if query:
        if st.session_state.step < len(questions):
            current_q = questions[st.session_state.step]
            st.markdown(f"### {current_q['q']}")
            answer = st.radio("Choose one:", current_q["options"], key=f"q{st.session_state.step}")

            if st.button("Next"):
                st.session_state.answers[current_q["q"]] = answer
                st.session_state.step += 1
                st.rerun()

        else:
            description = st.text_area("📝 Describe more about your disease")

            if st.button("Get AI Advice"):
                final_prompt = f"""
Symptoms: {query}
Answers: {st.session_state.answers}
Extra Description: {description}

Provide causes, precautions, medicines suggestion, and whether to see a doctor.
"""
                with st.spinner("Analyzing..."):
                    response = generate_response(final_prompt)
                    st.success("AI Medical Advice")
                    st.write(response)
                    text_to_speech(response)

# ---------------- TAB 2 ----------------
with tab2:
    if st.button("Search Doctors"):
        if user_location:
            query_map = urllib.parse.quote(f"doctor near {user_location}")
            maps_url = f"https://www.google.com/maps/search/{query_map}"
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
