import streamlit as st
from groq import Groq
import urllib.parse
from googletrans import Translator
from PIL import Image

# -------------------------------
# LOAD API KEY
# -------------------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

# -------------------------------
# INIT
# -------------------------------
client = Groq(api_key=GROQ_API_KEY)
translator = Translator()

LLAMA_MODEL = "llama-3.1-8b-instant"

# -------------------------------
# LANGUAGE OPTIONS (YOUR VERSION)
# -------------------------------
languages = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Marathi (मराठी)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Bengali (বাংলা)": "bn",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Assamese (অসমীয়া)": "as",
    "Urdu (اردو)": "ur",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml"
}

selected_lang = st.sidebar.selectbox("🌍 Select Language", list(languages.keys()))
lang_code = languages[selected_lang]

# -------------------------------
# FUNCTION
# -------------------------------
def generate_groq_response(user_message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Provide general health guidance only. Do not diagnose."},
                {"role": "user", "content": user_message}
            ],
            model=LLAMA_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺")

st.title("🩺 AI Medical Assistant")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2 = st.tabs(["🩺 Health Assistant", "📍 Nearby Doctors"])

# -------------------------------
# TAB 1
# -------------------------------
with tab1:
    user_query = st.text_area("Enter your symptoms:")

    uploaded_file = st.file_uploader("📷 Upload image", type=["jpg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image)

    if st.button("Get Advice"):
        if not user_query.strip():
            st.warning("Enter your query")
        else:
            with st.spinner("Analyzing..."):

                # SAFE TRANSLATE INPUT
                try:
                    translated_input = translator.translate(user_query, dest="en").text
                except:
                    translated_input = user_query

                response = generate_groq_response(translated_input)

                # SAFE TRANSLATE OUTPUT
                try:
                    final_response = translator.translate(response, dest=lang_code).text
                except:
                    final_response = response

                st.success("AI Response")
                st.write(final_response)

# -------------------------------
# TAB 2
# -------------------------------
with tab2:
    location = st.text_input("Enter location")

    if st.button("Search"):
        if location:
            query = urllib.parse.quote(f"doctor near {location}")
            st.markdown(f"https://www.google.com/maps/search/{query}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built with Groq + Streamlit")
