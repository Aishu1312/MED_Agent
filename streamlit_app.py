import streamlit as st
from groq import Groq
import urllib.parse

# -------------------------------
# LOAD API KEY
# -------------------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

# -------------------------------
# INIT CLIENT
# -------------------------------
client = Groq(api_key=GROQ_API_KEY)
LLAMA_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# -------------------------------
# FUNCTION
# -------------------------------
def generate_groq_response(user_message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant. Provide safe general health guidance. Avoid diagnosis."},
                {"role": "user", "content": user_message}
            ],
            model=LLAMA_MODEL,
            temperature=0.7,
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
# TAB 1: AI ASSISTANT
# -------------------------------
with tab1:
    st.subheader("Ask Health Questions")

    user_query = st.text_area(
        "Your health inquiry:",
        "I have a persistent cough and feel tired. What could be the reason?"
    )

    if st.button("Get Advice"):
        if not user_query.strip():
            st.warning("⚠️ Please enter your health inquiry.")
        else:
            # 🚨 Basic emergency detection
            if any(word in user_query.lower() for word in ["chest pain", "breathing difficulty", "unconscious"]):
                st.error("🚨 This may be serious. Seek immediate medical help.")

            with st.spinner("Analyzing symptoms..."):
                response = generate_groq_response(user_query)
                st.success("AI Response")
                st.write(response)

    st.markdown("---")
    st.warning("⚠️ This is not medical advice. Consult a doctor.")

# -------------------------------
# TAB 2: NEARBY DOCTORS
# -------------------------------
with tab2:
    st.subheader("Find Nearby Doctors")

    location = st.text_input("Enter your location (City / Area):", "Nagpur")

    doctor_type = st.selectbox(
        "Select doctor type:",
        ["General Physician", "Dentist", "Cardiologist", "Dermatologist", "ENT Specialist"]
    )

    if st.button("Search Doctors"):
        if not location.strip():
            st.warning("⚠️ Please enter a location.")
        else:
            query = f"{doctor_type} near {location}"
            encoded_query = urllib.parse.quote(query)

            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            hospital_url = f"https://www.google.com/maps/search/hospitals+near+{encoded_query}"
            pharmacy_url = f"https://www.google.com/maps/search/pharmacy+near+{encoded_query}"

            st.success("Doctors found nearby 👇")

            st.markdown(f"👉 [🔍 Search Doctors on Google Maps]({maps_url})")
            st.markdown(f"🏥 [Find Hospitals]({hospital_url})")
            st.markdown(f"💊 [Find Pharmacies]({pharmacy_url})")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built with Groq + Streamlit")
