# 🩺 MedAgent AI – Smart Virtual Healthcare Assistant

**Author(s):** Aishwarya Lala
**Affiliation:** St. Vincent Pallotti College of Engineering and Technology  
**Date:** April 2026  

---

## 📌 Abstract
MedAgent AI is an intelligent virtual healthcare assistant designed to provide users with preliminary medical guidance based on their symptoms. The system utilizes advanced Large Language Models (LLMs) powered by Groq to generate professional health-related responses in real time. It features a complete user authentication system and session persistence using a MongoDB database, allowing users to securely register, log in, and view their historical consultations. It supports multilingual communication across multiple Indian regional languages, making healthcare assistance more accessible to diverse users.  

The platform includes features such as secure login/registration, symptom-based multi-step questioning, voice input and output, image/report upload, consultation history tracking, nearby doctor search using Google Maps, and emergency contact details. The main objective of this project is to bridge the gap between patients and immediate healthcare guidance while reducing dependency on physical consultations for minor issues.  

The system is built using Streamlit for frontend deployment, integrates MongoDB for database management, and uses Groq's fast inference models for intelligent conversation. The results demonstrate that MedAgent AI provides quick, user-friendly, and efficient preliminary health assistance, making it a valuable tool in modern digital healthcare.

---

## 📖 Introduction
Healthcare accessibility remains a major challenge, especially in rural and semi-urban areas where immediate medical consultation is not always available. Many people ignore symptoms or fail to seek timely advice due to lack of awareness, distance, or cost constraints. MedAgent AI addresses this issue by offering an AI-powered virtual medical assistant capable of providing instant health-related guidance with high personalization and persistence.  

### 🎯 Key Features of MedAgent AI
- **Secure Authentication & Reload Persistence:** Users can register and log in to their personalized accounts. Passwords are securely hashed using SHA-256 with unique salts. Session tokens are generated and stored in MongoDB, maintaining login status across page reloads via URL query parameters.
- **Instant Multilingual Preliminary Advice:** Supports 10 languages (English, Hindi, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam). Both the assessment questions and AI responses adapt automatically to the user's selected language.
- **Symptom Assessment Questionnaire:** Interactive multi-step poll questions to collect specific details (pain severity, duration, fever presence) alongside text description.
- **Multimodal Uploads:** Support for uploading medical images or reports (PNG, JPG, JPEG, PDF) for reference during assessment.
- **Voice Interactions:** Hands-free voice symptom input using native Streamlit audio recording (`st.audio_input`) transcribed via Groq's Whisper API. Voice output guidance is generated using Google Text-to-Speech (gTTS).
- **Consultation History Dashboard:** All past consultations (symptoms, assessment answers, extra descriptions, and AI advice) are saved to MongoDB. Users can browse their history and re-listen to the advice anytime.
- **Nearby Doctor Recommendations:** Location-based doctor searches that generate direct links to Google Maps.
- **Emergency Helpline Access:** Instant access to crucial emergency numbers (Ambulance, Women Helpline, Child Helpline, General Emergency).

---

## ⚙️ Methodology
1. **User Sign Up / Sign In:** The user creates an account or logs in. On success, a session token is created in MongoDB and placed in the URL query parameters.
2. **Symptom & Multimodal Collection:** The user selects a language and inputs symptoms via text or voice. They can also upload reports/images.
3. **Structured Questionnaire:** The assistant takes the user through a series of context-aware follow-up questions translated to their selected language.
4. **AI Generation:** The accumulated symptoms, assessment answers, and description are packaged into a structured prompt and sent to the `llama-3.3-70b-versatile` model via Groq's API.
5. **Database Storage & Presentation:** The resulting AI advice is saved in MongoDB under the user's history, displayed on the interface, and played as audio.
6. **Auxiliary Features:** The user can search for nearby doctors using location parameters, look up emergency hotlines, or review past consultation history in the dashboard.

---

## 💻 Technical Stack

### Backend & Database
- **Python 3.11** – Core programming language.
- **MongoDB** – Database for storing user details, session tokens, and consultation history securely.
- **PyMongo** – Driver to establish connection and run queries against MongoDB database.

### Frontend & UI
- **Streamlit** – Web framework for rendering the user interface, sidebar settings, and interactive tabs.
- **HTML/CSS** – Custom embedded stylesheets for premium glassmorphic and dark mode styling.

### AI & Speech Models
- **Groq API** – High-speed inference engine running:
  - `llama-3.3-70b-versatile` for clinical analysis and medical guidance.
  - `whisper-large-v3` for speech-to-text transcription of voice symptoms.
- **gTTS (Google Text-to-Speech)** – Generates audio responses from the AI-generated health advice.

### Utility Libraries
- **python-dotenv** – Local configuration of environment variables (`.env`).
- **Pillow (PIL)** – Rendering and validating uploaded medical reports or symptom images.
- **urllib** – URL encoding for Google Maps integration.

---

## 🚀 Setup and Installation Guide

Follow these steps to set up and run MedAgent AI locally:

### 1. Prerequisites
Ensure you have the following installed on your system:
- Python 3.11 or later
- A running MongoDB instance (either local or MongoDB Atlas)

### 2. Clone the Repository
```bash
git clone https://github.com/Aishu1312/MED_Agent.git
cd MED_Agent
```

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a file named `.env` in the root of the project and add the following keys:
```env
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URI=your_mongodb_connection_uri_here
```
> [!NOTE]
> If deploying to Streamlit Cloud, you can configure these secrets under **Settings > Secrets** in the Streamlit Cloud Dashboard using the same environment key names.

### 6. Run the Application
```bash
streamlit run streamlit_app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## ⚠️ Limitations
- **Preliminary Guidance Only:** The system does not diagnose diseases and cannot replace professional medical consults.
- **AI Accuracy Risk:** AI-generated advice may contain errors or hallucinations. Users must always verify with a clinician.
- **Audio Sensitivity:** Whisper transcription quality depends on microphone and background noise levels.
- **Dependency on Connectivity:** Live internet access is required to access MongoDB and Groq API endpoints.

---

## 🔮 Future Scope
- Integration with hospital APIs for direct doctor appointments and scheduling.
- Advanced medical report parsing using computer vision models (e.g., LLaVA or GPT-4o-mini).
- Continuous tracking of health metrics via wearable API integrations (e.g., Apple Health, Fitbit).
- Secure encrypted patient-doctor video consultations inside the platform.

---

## ✅ Conclusion
MedAgent AI is a modern virtual healthcare assistant designed to bridge accessibility gaps in digital health. By combining state-of-the-art LLMs, fast database persistence, multi-lingual translations, and voice capabilities, it offers an engaging and informative first-level support tool. While it doesn't replace standard clinical assessments, it marks a significant step forward in making digital healthcare solutions persistent, interactive, and universally accessible.
