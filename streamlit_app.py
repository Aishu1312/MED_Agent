import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
from gtts import gTTS
import os
from streamlit_mic_recorder import mic_recorder   # ✅ ADDED

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="MedAgent AI", page_icon="🩺", layout="wide")

# ----------------------------
# CSS
# ----------------------------
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

# ----------------------------
# API KEY
# ----------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

LLAMA_MODEL = "llama-3.1-8b-instant"

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
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    user_location = st.text_input("📍 Enter City / Location")

# ----------------------------
# HEADER
# ----------------------------
st.markdown('<div class="big-title">🩺 MedAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Smart AI Healthcare Assistant</div>', unsafe_allow_html=True)

# ----------------------------
# FUNCTION
# ----------------------------
def generate_response(prompt):
    completion = client.chat.completions.create(
        model=LLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a professional AI doctor.
Ask only ONE question at a time.
Provide poll-style options where possible.
After enough answers, provide medical advice.
"""
            },
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def text_to_speech(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    file_path = "response.mp3"
    tts.save(file_path)
    audio_file = open(file_path, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

# ----------------------------
# TABS
# ----------------------------
tab1, tab2, tab3 = st.tabs(["💬 AI Doctor", "📍 Nearby Doctors", "🚑 Emergency"])

# ----------------------------
# TAB 1
# ----------------------------
with tab1:
    st.markdown("### Describe your symptoms")

    # ✅ MIC OPTION ADDED
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key="recorder"
    )

    if audio:
        st.success("✅ Voice recorded successfully!")
        st.audio(audio["bytes"])

    query = st.text_area("Enter your symptoms")

    uploaded_file = st.file_uploader("Upload image/report", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)

    if st.button("Get AI Advice"):
        if query:
            with st.spinner("Analyzing..."):
                response = generate_response(query)

                st.success("AI Medical Advice")
                st.write(response)

                # Voice output
                text_to_speech(response, lang_code)

# ----------------------------
# TAB 2
# ----------------------------
with tab2:
    if st.button("Search Doctors"):
        if user_location:
            query = urllib.parse.quote(f"doctor near {user_location}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(f"[🔍 Open Google Maps]({maps_url})")
        else:
            st.warning("Enter location in sidebar.")

# ----------------------------
# TAB 3
# ----------------------------
with tab3:
    st.write("📞 Ambulance: 108")
    st.write("📞 Emergency: 112")
    st.write("📞 Women Helpline: 1091")
    st.write("📞 Child Helpline: 1098")

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.caption("© 2026 MedAgent AI | Powered by Groq")
