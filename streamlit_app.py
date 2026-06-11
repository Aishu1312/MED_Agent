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
        "title": "MedAgent AI",
        "subtitle": "Your Smart AI Healthcare Assistant",
        "symptoms": "Enter your symptoms",
        "assessment": "Start Assessment",
        "upload": "Upload image/report",
        "doctor": "Nearby Doctors",
        "emergency": "Emergency",
        "next": "Next",
        "guidance": "Get Medical Guidance",
        "location": "Enter City / Location",
        "search_doctors": "Search Doctors",
        "new_consultation": "Start New Consultation"
    },

    "Hindi": {
        "title": "मेडएजेंट एआई",
        "subtitle": "आपका स्मार्ट स्वास्थ्य सहायक",
        "symptoms": "अपने लक्षण दर्ज करें",
        "assessment": "जांच शुरू करें",
        "upload": "रिपोर्ट अपलोड करें",
        "doctor": "नजदीकी डॉक्टर",
        "emergency": "आपातकाल",
        "next": "अगला",
        "guidance": "चिकित्सकीय सलाह प्राप्त करें",
        "location": "शहर / स्थान दर्ज करें",
        "search_doctors": "डॉक्टर खोजें",
        "new_consultation": "नई परामर्श शुरू करें"
    },

    "Marathi": {
        "title": "मेडएजंट एआय",
        "subtitle": "तुमचा स्मार्ट आरोग्य सहाय्यक",
        "symptoms": "तुमची लक्षणे लिहा",
        "assessment": "तपासणी सुरू करा",
        "upload": "अहवाल अपलोड करा",
        "doctor": "जवळचे डॉक्टर",
        "emergency": "आपत्कालीन सेवा",
        "next": "पुढे",
        "guidance": "वैद्यकीय मार्गदर्शन मिळवा",
        "location": "शहर / स्थान प्रविष्ट करा",
        "search_doctors": "डॉक्टर शोधा",
        "new_consultation": "नवीन सल्लामसलत सुरू करा"
    },

    "Gujarati": {
        "title": "મેડએજન્ટ AI",
        "subtitle": "તમારો સ્માર્ટ હેલ્થકેર સહાયક",
        "symptoms": "તમારા લક્ષણો દાખલ કરો",
        "assessment": "તપાસ શરૂ કરો",
        "upload": "રિપોર્ટ અપલોડ કરો",
        "doctor": "નજીકના ડોક્ટરો",
        "emergency": "આપાતકાલીન સેવા",
        "next": "આગળ",
        "guidance": "તબીબી માર્ગદર્શન મેળવો",
        "location": "શહેર / સ્થાન દાખલ કરો",
        "search_doctors": "ડોક્ટર શોધો",
        "new_consultation": "નવી સલાહ શરૂ કરો"
    },

    "Punjabi": {
        "title": "ਮੈਡਏਜੰਟ ਏਆਈ",
        "subtitle": "ਤੁਹਾਡਾ ਸਮਾਰਟ ਸਿਹਤ ਸਹਾਇਕ",
        "symptoms": "ਆਪਣੇ ਲੱਛਣ ਦਰਜ ਕਰੋ",
        "assessment": "ਜਾਂਚ ਸ਼ੁਰੂ ਕਰੋ",
        "upload": "ਰਿਪੋਰਟ ਅੱਪਲੋਡ ਕਰੋ",
        "doctor": "ਨਜ਼ਦੀਕੀ ਡਾਕਟਰ",
        "emergency": "ਐਮਰਜੈਂਸੀ",
        "next": "ਅੱਗੇ",
        "guidance": "ਮੈਡੀਕਲ ਸਲਾਹ ਪ੍ਰਾਪਤ ਕਰੋ",
        "location": "ਸ਼ਹਿਰ / ਸਥਾਨ ਦਰਜ ਕਰੋ",
        "search_doctors": "ਡਾਕਟਰ ਲੱਭੋ",
        "new_consultation": "ਨਵੀਂ ਸਲਾਹ ਸ਼ੁਰੂ ਕਰੋ"
    },

    "Bengali": {
        "title": "মেডএজেন্ট এআই",
        "subtitle": "আপনার স্মার্ট স্বাস্থ্য সহায়ক",
        "symptoms": "আপনার উপসর্গ লিখুন",
        "assessment": "পরীক্ষা শুরু করুন",
        "upload": "রিপোর্ট আপলোড করুন",
        "doctor": "নিকটবর্তী ডাক্তার",
        "emergency": "জরুরি পরিষেবা",
        "next": "পরবর্তী",
        "guidance": "চিকিৎসা পরামর্শ নিন",
        "location": "শহর / অবস্থান লিখুন",
        "search_doctors": "ডাক্তার খুঁজুন",
        "new_consultation": "নতুন পরামর্শ শুরু করুন"
    },

    "Tamil": {
        "title": "மெட் ஏஜென்ட் AI",
        "subtitle": "உங்கள் ஸ்மார்ட் சுகாதார உதவியாளர்",
        "symptoms": "உங்கள் அறிகுறிகளை உள்ளிடவும்",
        "assessment": "பரிசோதனையை தொடங்கவும்",
        "upload": "அறிக்கையை பதிவேற்றவும்",
        "doctor": "அருகிலுள்ள மருத்துவர்கள்",
        "emergency": "அவசரநிலை",
        "next": "அடுத்து",
        "guidance": "மருத்துவ ஆலோசனை பெறவும்",
        "location": "நகரம் / இடத்தை உள்ளிடவும்",
        "search_doctors": "மருத்துவரை தேடுங்கள்",
        "new_consultation": "புதிய ஆலோசனையை தொடங்கவும்"
    },

    "Telugu": {
        "title": "మెడ్ ఏజెంట్ AI",
        "subtitle": "మీ స్మార్ట్ ఆరోగ్య సహాయకుడు",
        "symptoms": "మీ లక్షణాలను నమోదు చేయండి",
        "assessment": "పరీక్ష ప్రారంభించండి",
        "upload": "రిపోర్ట్ అప్లోడ్ చేయండి",
        "doctor": "సమీప వైద్యులు",
        "emergency": "అత్యవసర సేవలు",
        "next": "తదుపరి",
        "guidance": "వైద్య సలహా పొందండి",
        "location": "నగరం / ప్రదేశం నమోదు చేయండి",
        "search_doctors": "డాక్టర్‌ను వెతకండి",
        "new_consultation": "కొత్త సంప్రదింపును ప్రారంభించండి"
    },

    "Kannada": {
        "title": "ಮೆಡ್ ಏಜೆಂಟ್ AI",
        "subtitle": "ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಆರೋಗ್ಯ ಸಹಾಯಕ",
        "symptoms": "ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ನಮೂದಿಸಿ",
        "assessment": "ಪರಿಶೀಲನೆ ಪ್ರಾರಂಭಿಸಿ",
        "upload": "ವರದಿಯನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "doctor": "ಹತ್ತಿರದ ವೈದ್ಯರು",
        "emergency": "ತುರ್ತು ಸೇವೆ",
        "next": "ಮುಂದೆ",
        "guidance": "ವೈದ್ಯಕೀಯ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ",
        "location": "ನಗರ / ಸ್ಥಳವನ್ನು ನಮೂದಿಸಿ",
        "search_doctors": "ವೈದ್ಯರನ್ನು ಹುಡುಕಿ",
        "new_consultation": "ಹೊಸ ಸಲಹೆ ಪ್ರಾರಂಭಿಸಿ"
    },

    "Malayalam": {
        "title": "മെഡ് ഏജന്റ് AI",
        "subtitle": "നിങ്ങളുടെ സ്മാർട്ട് ആരോഗ്യ സഹായി",
        "symptoms": "നിങ്ങളുടെ ലക്ഷണങ്ങൾ നൽകുക",
        "assessment": "പരിശോധന ആരംഭിക്കുക",
        "upload": "റിപ്പോർട്ട് അപ്‌ലോഡ് ചെയ്യുക",
        "doctor": "സമീപ ഡോക്ടർമാർ",
        "emergency": "അടിയന്തര സേവനം",
        "next": "അടുത്തത്",
        "guidance": "വൈദ്യോപദേശം നേടുക",
        "location": "നഗരം / സ്ഥലം നൽകുക",
        "search_doctors": "ഡോക്ടറെ കണ്ടെത്തുക",
        "new_consultation": "പുതിയ കൺസൾട്ടേഷൻ ആരംഭിക്കുക"
    }
}

if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙ Settings")
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    t = translations[selected_lang]
    st.session_state.language = selected_lang
    user_location = st.text_input(
    f'📍 {t["location"]}'
)

# ---------------- HEADER ----------------
st.markdown(
    f'<div class="big-title">🩺 {t["title"]}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">{t["subtitle"]}</div>',
    unsafe_allow_html=True
)

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

if st.button(t["new_consultation"]):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.assessment_started = False
    st.rerun()


# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "💬 AI Doctor",
    f"📍 {t['doctor']}",
    f"🚑 {t['emergency']}"
])

# ---------------- TAB 1 ----------------
with tab1:

    st.markdown(f"### {t['symptoms']}")

    # TEXT INPUT
      query = st.text_area(
        t["symptoms"],
        placeholder=t["symptoms"]
    )

    if st.button(f"🩺 {t['assessment']}"):

        if not query.strip():
            st.warning("Please enter your symptoms.")
        else:
            st.session_state.query = query
            st.session_state.assessment_started = True

    # FILE UPLOAD
uploaded_file = st.file_uploader(
        t["upload"],
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

            answer = st.radio(
                "Choose one:",
                current_q["options"],
                key=f"q{st.session_state.step}"
            )

            if st.button(t["next"]):

                st.session_state.answers[current_q["q"]] = answer
                st.session_state.step += 1
                st.rerun()

        else:

            description = st.text_area(
                "📝 Describe more about your condition"
            )

            if st.button(f"💡 {t['guidance']}"):

                final_prompt = f"""
Symptoms: {st.session_state.query}

Answers:
{st.session_state.answers}

Extra Description:
{description}

Provide:
1. Possible causes
2. Severity level
3. Precautions
4. Home remedies
5. Diet suggestions
6. Whether doctor consultation is needed

Answer completely in {selected_lang}.
"""

                with st.spinner("Analyzing..."):

                    response = generate_response(final_prompt)

                    st.success("AI Medical Advice")
                    st.write(response)

                    text_to_speech(response)

# ---------------- TAB 2 ----------------
with tab2:

    if st.button(t["search_doctors"]):

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
