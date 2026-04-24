import streamlit as st
from groq import Groq
import urllib.parse
from googletrans import Translator
import speech_recognition as sr
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

LLAMA_MODEL = "llama3-8b-8192"

# -------------------------------
# LANGUAGE OPTIONS
# -------------------------------
languages = {
    "English": "en",
    "Hindi": "hi"
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
                {
                    "role": "system",
                    "content": "You are a medical assistant. Provide general health guidance only. Do not diagnose. Suggest consulting a doctor."
                },
                {"role": "user", "content": user_message}
            ],
            model=LLAMA_MODEL,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# -------------------------------
# VOICE INPUT FUNCTION
# -------------------------------
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            return text
        except:
            return "❌ Could not understand audio"

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺")

st.title("🩺 AI Medical Assistant")
st.caption("Smart • Multilingual • Voice Enabled")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2 = st.tabs(["🩺 Health Assistant", "📍 Nearby Doctors"])

# -------------------------------
# TAB 1
# -------------------------------
with tab1:
    st.subheader("Ask Health Questions")

    # TEXT INPUT
    user_query = st.text_area("Enter your symptoms:")

    # VOICE INPUT
    if st.button("🎤 Speak"):
        user_query = get_voice_input()
        st.write("You said:", user_query)

    # IMAGE UPLOAD
    uploaded_file = st.file_uploader("📷 Upload symptom image", type=["jpg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # BUTTON
    if st.button("Get Advice"):
        if not user_query.strip():
            st.warning("⚠️ Please enter your query.")
        else:
            # Emergency detection
            emergency_keywords = [
                "chest pain", "breathing difficulty", "unconscious",
                "seizure", "heart attack", "stroke"
            ]

            if any(word in user_query.lower() for word in emergency_keywords):
                st.error("🚨 Emergency! Please seek immediate medical help.")

            with st.spinner("Analyzing..."):
                # Translate to English for AI
                translated_input = translator.translate(user_query, dest="en").text

                response = generate_groq_response(translated_input)

                # Translate back
                final_response = translator.translate(response, dest=lang_code).text

                st.success("AI Response")
                st.write(final_response)

    st.markdown("---")
    st.warning("⚠️ This is not medical advice. Always consult a doctor.")

# -------------------------------
# TAB 2
# -------------------------------
with tab2:
    st.subheader("Find Nearby Doctors")

    location = st.text_input("Enter location:")

    doctor_type = st.selectbox(
        "Select doctor type:",
        ["General Physician", "Dentist", "Cardiologist", "Dermatologist", "ENT Specialist"]
    )

    if st.button("Search"):
        if not location.strip():
            st.warning("⚠️ Enter location")
        else:
            query = f"{doctor_type} near {location}"
            encoded_query = urllib.parse.quote(query)

            st.success("Results 👇")

            st.markdown(f"[🔍 Doctors](https://www.google.com/maps/search/{encoded_query})")
            st.markdown(f"[🏥 Hospitals](https://www.google.com/maps/search/hospitals+near+{encoded_query})")
            st.markdown(f"[💊 Pharmacies](https://www.google.com/maps/search/pharmacy+near+{encoded_query})")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built with ❤️ using Groq + Streamlit")
