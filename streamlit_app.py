import streamlit as st
import urllib.parse
from PIL import Image

# -------------------------------
# SAFE IMPORT FOR GROQ
# -------------------------------
try:
    from groq import Groq
except ImportError:
    st.error("❌ Groq package is not installed. Add `groq` to requirements.txt")
    st.stop()

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺")

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

LLAMA_MODEL = "llama-3.1-8b-instant"

# -------------------------------
# FUNCTION
# -------------------------------
def generate_groq_response(user_message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Provide general health guidance only. Do not diagnose."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model=LLAMA_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# -------------------------------
# TITLE
# -------------------------------
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

    uploaded_file = st.file_uploader("📷 Upload image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Get Advice"):
        if not user_query.strip():
            st.warning("⚠️ Enter your query")
        else:
            with st.spinner("Analyzing..."):
                response = generate_groq_response(user_query)

                st.success("AI Response")
                st.write(response)

# -------------------------------
# TAB 2
# -------------------------------
with tab2:
    location = st.text_input("Enter location")

    if st.button("Search"):
        if location:
            query = urllib.parse.quote(f"doctor near {location}")
            maps_url = f"https://www.google.com/maps/search/{query}"
            st.markdown(f"[🔍 Open Google Maps]({maps_url})")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built with Groq + Streamlit")
