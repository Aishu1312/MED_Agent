import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
from gtts import gTTS
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import hashlib
import secrets
from datetime import datetime, timezone

# Load local environment variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(script_dir, ".env"), override=True)

# ---------------- DATABASE CONNECTION ----------------
MONGODB_URI = os.environ.get("MONGODB_URI")
if not MONGODB_URI:
    try:
        MONGODB_URI = st.secrets["MONGODB_URI"]
    except Exception:
        pass

db_enabled = False
db = None
db_error = None

if MONGODB_URI and MONGODB_URI != "your_mongodb_connection_uri_here":
    try:
        # Establish connection with a 3-second timeout for server selection
        client_db = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
        # Force a connection check
        client_db.server_info()
        db = client_db["medagent_db"]
        db_enabled = True
    except Exception as e:
        db_error = str(e)
else:
    db_error = "MONGODB_URI is not set in the environment or .env file."

# ---------------- DATABASE HELPERS ----------------
def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
    return hash_obj.hexdigest(), salt

def register_user(username, password):
    if not db_enabled:
        return False, f"Database not connected. ({db_error})"
    
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password cannot be empty."
        
    try:
        existing_user = db["users"].find_one({"username": username})
        if existing_user:
            return False, "Username already exists."
            
        password_hash, salt = hash_password(password)
        db["users"].insert_one({
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now(timezone.utc)
        })
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def login_user(username, password):
    if not db_enabled:
        return False, f"Database not connected. ({db_error})"
        
    username = username.strip().lower()
    try:
        user_doc = db["users"].find_one({"username": username})
        if not user_doc:
            return False, "Invalid username or password."
            
        password_hash, _ = hash_password(password, user_doc["salt"])
        if password_hash == user_doc["password_hash"]:
            return True, "Login successful!"
        else:
            return False, "Invalid username or password."
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def save_consultation(username, symptoms, answers, description, response, language):
    if not db_enabled:
        return False
    try:
        db["history"].insert_one({
            "username": username.strip().lower(),
            "timestamp": datetime.now(timezone.utc),
            "symptoms": symptoms,
            "answers": answers,
            "description": description,
            "response": response,
            "language": language
        })
        return True
    except Exception:
        return False

def get_user_history(username):
    if not db_enabled:
        return []
    try:
        cursor = db["history"].find({"username": username.strip().lower()}).sort("timestamp", -1)
        return list(cursor)
    except Exception:
        return []

def create_session(username):
    if not db_enabled:
        return None
    token = secrets.token_hex(32)
    from datetime import timedelta
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    try:
        db["sessions"].insert_one({
            "token": token,
            "username": username.strip().lower(),
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at
        })
        return token
    except Exception:
        return None

def verify_session(token):
    if not db_enabled or not token:
        return None
    try:
        session_doc = db["sessions"].find_one({"token": token})
        if session_doc:
            if session_doc["expires_at"] > datetime.now(timezone.utc):
                return session_doc["username"]
            else:
                db["sessions"].delete_one({"token": token})
        return None
    except Exception:
        return None

def delete_session(token):
    if not db_enabled or not token:
        return False
    try:
        db["sessions"].delete_one({"token": token})
        return True
    except Exception:
        return False


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
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        pass

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

# ---------------- SESSION STATE FOR AUTH ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Auto login check from query parameters session token
if not st.session_state.logged_in:
    session_token = st.query_params.get("session_token")
    if session_token:
        username = verify_session(session_token)
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1 style="color: #00E5FF; font-size: 48px; font-weight: bold; margin-bottom: 5px;">🩺 MedAgent AI</h1>
        <p style="color: #CBD5E1; font-size: 18px; margin-bottom: 30px;">Smart Multilingual Healthcare Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not db_enabled:
        st.error(f"⚠️ Database not connected. Please configure a valid MONGODB_URI in your .env file to enable authentication. (Error: {db_error})")
        st.stop()
        
    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with auth_tab1:
        st.subheader("Login to your Account")
        login_user_input = st.text_input("Username", key="login_username").strip()
        login_pass_input = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if not login_user_input or not login_pass_input:
                st.error("Please enter both username and password.")
            else:
                success, msg = login_user(login_user_input, login_pass_input)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user_input
                    
                    # Create and store session token in query params for reload persistence
                    token = create_session(login_user_input)
                    if token:
                        st.query_params["session_token"] = token
                        
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
    with auth_tab2:
        st.subheader("Create a New Account")
        reg_user_input = st.text_input("Username", key="reg_username").strip()
        reg_pass_input = st.text_input("Password", type="password", key="reg_password")
        reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        if st.button("Register", type="primary", use_container_width=True):
            if not reg_user_input or not reg_pass_input:
                st.error("Username and password fields cannot be empty.")
            elif reg_pass_input != reg_pass_confirm:
                st.error("Passwords do not match.")
            elif len(reg_pass_input) < 4:
                st.error("Password must be at least 4 characters long.")
            else:
                success, msg = register_user(reg_user_input, reg_pass_input)
                if success:
                    st.success(msg + " Please switch to the Login tab to sign in.")
                else:
                    st.error(msg)
                    
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙ Settings")
    st.markdown(f"👤 **Logged in as:** `{st.session_state.username}`")
    
    selected_lang = st.selectbox("🌍 Select Language", list(languages.keys()))
    lang_code = languages[selected_lang]
    t = translations[selected_lang]
    st.session_state.language = selected_lang
    user_location = st.text_input(
        f'📍 {t["location"]}'
    )
    
    if st.button("🚪 Logout", use_container_width=True):
        # Delete session from database and URL query parameters
        token = st.query_params.get("session_token")
        if token:
            delete_session(token)
            if "session_token" in st.query_params:
                del st.query_params["session_token"]
                
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.assessment_started = False
        st.rerun()

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
    if not client:
        return "Error: Groq API client is not initialized. Please configure your GROQ_API_KEY in the code."
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

if "voice_transcription" not in st.session_state:
    st.session_state.voice_transcription = ""

if st.button(t["new_consultation"]):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.assessment_started = False
    st.session_state.voice_transcription = ""

    if "query" in st.session_state:
        del st.session_state["query"]

    st.rerun()


# ---------------- TABS ----------------
history_translations = {
    "English": "History",
    "Hindi": "इतिहास",
    "Marathi": "इतिहास",
    "Gujarati": "ઇતિહાસ",
    "Punjabi": "ਇਤਿਹਾਸ",
    "Bengali": "ইতিহাস",
    "Tamil": "வரலாறு",
    "Telugu": "చరిత్ర",
    "Kannada": "ಇತಿಹಾಸ",
    "Malayalam": "ചриത്രം"
}
history_tab_title = history_translations.get(selected_lang, "History")

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 AI Doctor",
    f"📍 {t['doctor']}",
    f"🚑 {t['emergency']}",
    f"📜 {history_tab_title}"
])

# ---------------- TAB 1 ----------------
with tab1:

    if not st.session_state.assessment_started:
        st.markdown(f"### {t['symptoms']}")

        # Select input method
        input_method = st.radio(
            "Select Input Method:",
            ["Text Input 📝", "Voice Input 🎤"],
            horizontal=True,
            key="symptoms_input_method"
        )

        query = ""

        if input_method == "Text Input 📝":
            # TEXT INPUT
            query = st.text_area(
                t["symptoms"],
                placeholder=t["symptoms"],
                key="symptoms_text_area"
            )
            # Clear voice transcription if they switch back to text
            st.session_state.voice_transcription = ""
        else:
            # VOICE INPUT
            audio_val = st.audio_input("Record your symptoms:")
            if audio_val:
                if not st.session_state.voice_transcription:
                    if not client:
                        st.error("Error: Groq API client is not initialized. Please configure your GROQ_API_KEY.")
                    else:
                        with st.spinner("Transcribing your voice..."):
                            try:
                                audio_bytes = audio_val.read()
                                # Call Groq Whisper API for translation/transcription
                                transcription = client.audio.transcriptions.create(
                                    file=("audio.wav", audio_bytes),
                                    model="whisper-large-v3",
                                    language=lang_code
                                )
                                st.session_state.voice_transcription = transcription.text
                            except Exception as e:
                                st.error(f"Speech-to-Text Error: {str(e)}")
            
            if st.session_state.voice_transcription:
                query = st.text_area(
                    "Review/edit your recorded symptoms:",
                    value=st.session_state.voice_transcription,
                    key="voice_text_edit"
                )

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

        # START ASSESSMENT BUTTON
        if st.button(f"🩺 {t['assessment']}"):
            if not query.strip():
                st.warning("Please enter or record your symptoms.")
            else:
                st.session_state.query = query
                st.session_state.assessment_started = True
                st.session_state.voice_transcription = ""
                st.rerun()
    else:
        st.info(f"📋 **Current symptoms:** {st.session_state.query}")

    # POLL QUESTIONS
    questions_by_lang = {
        "English": [
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
        ],
        "Hindi": [
            {
                "q": "आपके दर्द की तीव्रता क्या है?",
                "options": ["1-3 हल्का", "4-6 मध्यम", "7-10 गंभीर", "पता नहीं"]
            },
            {
                "q": "आपको ये लक्षण कब से हैं?",
                "options": ["कुछ मिनट", "कुछ घंटे", "1 दिन", "कई दिन"]
            },
            {
                "q": "क्या आपको बुखार है?",
                "options": ["हाँ", "नहीं", "पता नहीं"]
            }
        ],
        "Marathi": [
            {
                "q": "तुमच्या वेदनेची तीव्रता काय आहे?",
                "options": ["1-3 सौम्य", "4-6 मध्यम", "7-10 तीव्र", "नक्की माहिती नाही"]
            },
            {
                "q": "तुम्हाला ही लक्षणे कधीपासून आहेत?",
                "options": ["काही मिनिटे", "काही तास", "1 दिवस", "बरेच दिवस"]
            },
            {
                "q": "तुम्हाला ताप आहे का?",
                "options": ["होय", "नाही", "नक्की माहिती नाही"]
            }
        ],
        "Gujarati": [
            {
                "q": "તમારા દુખાવાની તીવ્રતા શું છે?",
                "options": ["1-3 હળવો", "4-6 મધ્યમ", "7-10 તીવ્ર", "ખબર નથી"]
            },
            {
                "q": "તમને આ લક્ષણો ક્યારથી છે?",
                "options": ["થોડી મિનિટો", "થોડા કલાકો", "1 દિવસ", "ઘણા દિવસો"]
            },
            {
                "q": "શું તમને તાવ છે?",
                "options": ["હા", "ના", "ખબર નથી"]
            }
        ],
        "Punjabi": [
            {
                "q": "ਤੁਹਾਡੇ ਦਰਦ ਦੀ ਤੀਬਰਤਾ ਕੀ ਹੈ?",
                "options": ["1-3 ਹਲਕਾ", "4-6 ਦਰਮਿਆਨਾ", "7-10 ਗੰਭੀਰ", "ਪਤਾ ਨਹੀਂ"]
            },
            {
                "q": "ਤੁਹਾਨੂੰ ਇਹ ਲੱਛਣ ਕਦੋਂ ਤੋਂ ਹਨ?",
                "options": ["ਕੁਝ ਮਿੰਟ", "ਕੁਝ ਘੰਟੇ", "1 ਦਿਨ", "ਕਈ ਦਿਨ"]
            },
            {
                "q": "ਕੀ ਤੁਹਾਨੂੰ ਬੁਖਾਰ ਹੈ?",
                "options": ["ਹਾਂ", "ਨਹੀਂ", "ਪਤਾ ਨਹੀਂ"]
            }
        ],
        "Bengali": [
            {
                "q": "আপনার ব্যথার তীব্রতা কতটা?",
                "options": ["১-৩ মৃদু", "৪-৬ মাঝারি", "৭-১০ তীব্র", "নিশ্চিত নই"]
            },
            {
                "q": "আপনার এই উপসর্গগুলি কতদিন ধরে আছে?",
                "options": ["কয়েক মিনিট", "কয়েক ঘন্টা", "১ দিন", "কয়েক দিন"]
            },
            {
                "q": "আপনার কি জ্বর আছে?",
                "options": ["হ্যাঁ", "না", "নিশ্চিত নই"]
            }
        ],
        "Tamil": [
            {
                "q": "உங்கள் வலியின் தீவிரம் என்ன?",
                "options": ["1-3 லேசானது", "4-6 மிதமானது", "7-10 கடுமையானது", "நிச்சயமில்லை"]
            },
            {
                "q": "இந்த அறிகுறிகள் உங்களுக்கு எவ்வளவு காலமாக உள்ளன?",
                "options": ["சில நிமிடங்கள்", "சில மணிநேரங்கள்", "1 நாள்", "பல நாட்கள்"]
            },
            {
                "q": "உங்களுக்கு காய்ச்சல் இருக்கிறதா?",
                "options": ["ஆம்", "இல்லை", "நிச்சயமில்லை"]
            }
        ],
        "Telugu": [
            {
                "q": "మీ నొప్పి తీవ్రత ఎంత ఉంది?",
                "options": ["1-3 స్వల్పం", "4-6 మధ్యస్థం", "7-10 తీవ్రం", "తెలియదు"]
            },
            {
                "q": "మీకు ఈ లక్షణాలు ఎంతకాలంగా ఉన్నాయి?",
                "options": ["కొన్ని నిమిషాలు", "కొన్ని గంటలు", "1 రోజు", "చాలా రోజులు"]
            },
            {
                "q": "మీకు జ్వరం ఉందా?",
                "options": ["అవును", "కాదు", "తెలియదు"]
            }
        ],
        "Kannada": [
            {
                "q": "ನಿಮ್ಮ ನೋವಿನ ತೀವ್ರತೆ ಎಷ್ಟಿದೆ?",
                "options": ["1-3 ಮೃದು", "4-6 ಮಧ್ಯಮ", "7-10 ತೀವ್ರ", "ಗೊತ್ತಿಲ್ಲ"]
            },
            {
                "q": "ನಿಮಗೆ ಈ ಲಕ್ಷಣಗಳು ಎಷ್ಟು ಸಮಯದಿಂದ ಇವೆ?",
                "options": ["ಕೆಲವು ನಿಮಿಷಗಳು", "ಕೆಲವು ಗಂಟೆಗಳು", "1 ದಿನ", "ಹಲವು ದಿನಗಳು"]
            },
            {
                "q": "ನಿಮಗೆ ಜ್ವರ ಇದೆಯೇ?",
                "options": ["ಹೌದು", "ಇಲ್ಲ", "ಗೊತ್ತಿಲ್ಲ"]
            }
        ],
        "Malayalam": [
            {
                "q": "നിങ്ങളുടെ വേദനയുടെ തീവ്രത എത്രയാണ്?",
                "options": ["1-3 ലഘുവായത്", "4-6 മിതമായത്", "7-10 കഠിനമായത്", "ഉറപ്പില്ല"]
            },
            {
                "q": "നിങ്ങൾക്ക് ഈ ലക്ഷണങ്ങൾ എത്ര നാളായി ഉണ്ട്?",
                "options": ["കുറച്ചു മിനിറ്റുകൾ", "കുറച്ചു മണിക്കൂറുകൾ", "1 ദിവസം", "പല ദിവസങ്ങൾ"]
            },
            {
                "q": "നിങ്ങൾക്ക് പനിയുണ്ടോ?",
                "options": ["ഉണ്ട്", "ഇല്ല", "ഉറപ്പില്ല"]
            }
        ]
    }
    questions = questions_by_lang.get(selected_lang, questions_by_lang["English"])

    # SHOW QUESTIONS ONLY AFTER START ASSESSMENT
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

            desc_labels = {
                "English": "📝 Describe more about your condition",
                "Hindi": "📝 अपनी स्थिति के बारे में अधिक विस्तार से बताएं",
                "Marathi": "📝 तुमच्या स्थितीबद्दल अधिक माहिती सांगा",
                "Gujarati": "📝 તમારી સ્થિતિ વિશે વધુ વિગતવાર વર્ણન કરો",
                "Punjabi": "📝 ਆਪਣੀ ਸਥਿਤੀ ਬਾਰੇ ਹੋਰ ਵਿਸਥਾਰ ਨਾਲ ਦੱਸੋ",
                "Bengali": "📝 আপনার অবস্থা সম্পর্কে আরও বিস্তারিত বর্ণনা করুন",
                "Tamil": "📝 உங்கள் உடல்நிலையைப் பற்றி மேலும் விவரிக்கவும்",
                "Telugu": "📝 మీ పరిస్థితి గురించి మరింత వివరంగా వివరించండి",
                "Kannada": "📝 ನಿಮ್ಮ ಸ್ಥಿತಿಯ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ವಿವರಿಸಿ",
                "Malayalam": "📝 നിങ്ങളുടെ രോഗാവസ്ഥയെക്കുറിച്ച് കൂടുതൽ വിവരിക്കുക"
            }
            desc_label = desc_labels.get(selected_lang, desc_labels["English"])

            description = st.text_area(desc_label)

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

                    # Save consultation to MongoDB history
                    save_consultation(
                        username=st.session_state.username,
                        symptoms=st.session_state.query,
                        answers=st.session_state.answers,
                        description=description,
                        response=response,
                        language=selected_lang
                    )

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

# ---------------- TAB 4 ----------------
with tab4:
    st.markdown("### 📜 Your Consultation History")
    history_records = get_user_history(st.session_state.username)
    
    if not history_records:
        st.info("You don't have any previous consultations yet.")
    else:
        for idx, record in enumerate(history_records):
            timestamp_str = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            lang = record.get("language", "English")
            symptoms_preview = record.get("symptoms", "")[:50] + "..." if len(record.get("symptoms", "")) > 50 else record.get("symptoms", "")
            
            with st.expander(f"📅 {timestamp_str} | Symptoms: {symptoms_preview} ({lang})"):
                st.markdown(f"**Symptoms:** {record.get('symptoms')}")
                
                # Show answers
                st.markdown("**Assessment Answers:**")
                answers = record.get("answers", {})
                for q, a in answers.items():
                    st.markdown(f"- *{q}*: {a}")
                    
                extra_desc = record.get("description", "")
                if extra_desc:
                    st.markdown(f"**Additional Description:** {extra_desc}")
                    
                st.success("AI Medical Advice")
                st.write(record.get("response"))
                
                # TTS for history record
                if st.button(f"🔊 Listen to Advice #{idx+1}", key=f"tts_hist_{idx}"):
                    text_to_speech(record.get("response"))

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 MedAgent AI | Powered by Groq")
