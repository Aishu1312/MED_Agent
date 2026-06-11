import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
from gtts import gTTS

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
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()
LLAMA_MODEL = "llama-3.3-70b-versatile"

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

# ---------------- TRANSLATIONS ----------------
translations = {
"English": {
"symptoms": "Enter your symptoms",
"assessment": "Start Assessment",
"guidance": "Get Medical Guidance"
},

"Hindi": {
    "symptoms": "अपने लक्षण दर्ज करें",
    "assessment": "जांच शुरू करें",
    "guidance": "चिकित्सकीय सलाह प्राप्त करें"
},

"Marathi": {
    "symptoms": "तुमची लक्षणे लिहा",
    "assessment": "तपासणी सुरू करा",
    "guidance": "वैद्यकीय मार्गदर्शन मिळवा"
},

"Gujarati": {
    "symptoms": "તમારા લક્ષણો દાખલ કરો",
    "assessment": "તપાસ શરૂ કરો",
    "guidance": "તબીબી માર્ગદર્શન મેળવો"
},

"Punjabi": {
    "symptoms": "ਆਪਣੇ ਲੱਛਣ ਦਰਜ ਕਰੋ",
    "assessment": "ਜਾਂਚ ਸ਼ੁਰੂ ਕਰੋ",
    "guidance": "ਮੈਡੀਕਲ ਸਲਾਹ ਪ੍ਰਾਪਤ ਕਰੋ"
},

"Bengali": {
    "symptoms": "আপনার উপসর্গ লিখুন",
    "assessment": "পরীক্ষা শুরু করুন",
    "guidance": "চিকিৎসা পরামর্শ নিন"
},

"Tamil": {
    "symptoms": "உங்கள் அறிகுறிகளை உள்ளிடவும்",
    "assessment": "பரிசோதனையை தொடங்கவும்",
    "guidance": "மருத்துவ ஆலோசனை பெறவும்"
},

"Telugu": {
    "symptoms": "మీ లక్షణాలను నమోదు చేయండి",
    "assessment": "పరీక్ష ప్రారంభించండి",
    "guidance": "వైద్య సలహా పొందండి"
},

"Kannada": {
    "symptoms": "ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ನಮೂದಿಸಿ",
    "assessment": "ಪರಿಶೀಲನೆ ಪ್ರಾರಂಭಿಸಿ",
    "guidance": "ವೈದ್ಯಕೀಯ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ"
},

"Malayalam": {
    "symptoms": "നിങ്ങളുടെ ലക്ഷണങ്ങൾ നൽകുക",
    "assessment": "പരിശോധന ആരംഭിക്കുക",
    "guidance": "വൈദ്യോപദേശം നേടുക"
}
}


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    t = translations[selected_lang]
    user_location = st.text_input("📍 Enter City / Location")

# ---------------- HEADER ----------------
st.markdown('<div class="big-title">🩺 MedAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Smart AI Healthcare Assistant</div>', unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def generate_response(prompt):
    try:
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a professional healthcare assistant.

Always respond completely in {selected_lang}.

Provide:
1. Possible causes
2. Severity level (Low/Medium/High)
3. Precautions
4. Home remedies
5. Diet suggestions
6. Whether immediate medical attention is needed

Do not diagnose diseases.
Always advise consulting a qualified doctor.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Error generating response: {str(e)}"


# ---------------- TEXT TO SPEECH ----------------
import tempfile

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang=lang_code)
    except Exception:
        tts = gTTS(text=text, lang="en")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)

    with open(fp.name, "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# ---------------- SESSION STATE ----------------
if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "assessment_started" not in st.session_state:
    st.session_state.assessment_started = False

if st.button("Start New Consultation"):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.rerun()


# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["💬 AI Doctor", "📍 Nearby Doctors", "🚑 Emergency"])

# ---------------- TAB 1 ----------------
with tab1:
    st.markdown(f"### {t['symptoms']}")

    # TEXT INPUT
    query = st.text_area(
    "Enter your symptoms",
    placeholder="Example: Fever, headache, cough since 2 days"
)

if st.button(f"🩺 {t['assessment']}"):

    if not query.strip():
        st.warning("Please enter your symptoms.")
        st.stop()

    st.session_state.query = query
    st.session_state.assessment_started = True

    # FILE UPLOAD
    uploaded_file = st.file_uploader(
    "Upload image/report",
    type=["png", "jpg", "jpeg", "pdf"]
)

if uploaded_file:

    if uploaded_file.type.startswith("image"):
        try:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)
        except Exception:
            st.error("Invalid image file.")

    elif uploaded_file.type == "application/pdf":
        st.success("PDF uploaded successfully.")
        
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

    if st.session_state.assessment_started:
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

            if st.button(f"💡 {t['guidance']}"):
                final_prompt = f"""
Symptoms: {query}
Answers: {st.session_state.answers}
Extra Description: {description}

Provide:

1. Possible causes
2. Severity level (Low/Medium/High)
3. Precautions
4. Home remedies
5. Diet suggestions
6. Whether immediate medical care is needed

Answer in {selected_lang}.
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

            query_map = urllib.parse.quote(
                f"doctor near {user_location}"
            )

            maps_url = (
                f"https://www.google.com/maps/search/{query_map}"
            )

            st.markdown(
                f"[🔍 Open Google Maps]({maps_url})"
            )

        else:
            st.warning("Please enter a location.")

# ---------------- TAB 3 ----------------
with tab3:
    st.write("📞 Ambulance: 108")
    st.write("📞 Emergency: 112")
    st.write("📞 Women Helpline: 1091")
    st.write("📞 Child Helpline: 1098")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 MedAgent AI | Powered by Groq")
