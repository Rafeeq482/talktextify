import os
import streamlit as st
import azure.cognitiveservices.speech as speechsdk

# Azure Speech API configuration
subscription_key = "b32f134094a2432fa1293380952bfa61"
region = "eastus"

# Available languages and their respective codes
LANGUAGES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "Russian": "ru-RU",
    "Japanese": "ja-JP"
}

# Function to recognize speech
def recognize_speech_from_mic(language_code):
    """Recognize speech using Azure's Speech SDK with the selected language."""
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_recognition_language = language_code
    
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        st.error("No speech could be recognized.🎤🚫")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.error(f"Error: {cancellation_details.reason}, {cancellation_details.error_details}")
        return None

# Initialize the session state for history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Custom CSS for dark theme, white fonts, and dark blue button
st.markdown("""
    <style>
        body {
            background-color: #101820; /* Black-blue background */
        }
        .main {
            background-color: #1c1e22; /* Darker background for main area */
            padding: 30px;
            border-radius: 15px;
            max-width: 850px;
            margin: 0 auto;
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.5);
            font-family: 'Segoe UI', sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to top, #09203f 0%, #537895 100%);;
            }
        h1, h2, h3, p, label {
            color: #ffffff; /* White font color */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #00B4D8; /* Dark blue button */
            color: white;
            border-radius: 30px;
            padding: 10px 20px;
            font-size: 18px;
            border: none;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #104E8B; /* Darker blue on hover */
            transform: scale(1.05);
        }
        
        .stTextArea textarea {
            background-color: #212529;
            padding: 15px;
            border-radius: 15px;
            border: 1px solid #495057;
            font-size: 21px;
            color: #ffffff !important; /* White font for transcription area */
            transition: all 0.3s ease;
        }
        .stTextArea textarea:focus {
            border-color: #1E90FF;
            box-shadow: 0px 0px 8px rgba(30, 144, 255, 0.5);
        }
        .transcription-history {
            background-color: #212529; /* Dark background for transcription history */
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            color: #ffffff; /* White font for history */
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
            animation: slideIn 0.5s ease-out;
        }
        .transcription-history:hover {
            background-color: #1E90FF; /* Highlight history on hover */
            color: #ffffff;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .language-select label {
            color: #ffffff;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.markdown("<div><h1>TalkTextify : An Azure-Driven Speech Recognition System.</h1></div>", unsafe_allow_html=True)
st.markdown("<div><h2></h2></div>", unsafe_allow_html=True)

# Side-by-side layout for language selector and main functionality
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<h3>Select Language</h3>", unsafe_allow_html=True)
    selected_language = st.selectbox("Choose a language", list(LANGUAGES.keys()), key="language", label_visibility="collapsed")
    language_code = LANGUAGES[selected_language]

with col2:
    # State to control when listening starts and stops
    listening = st.empty()  # Placeholder for showing the "Listening" message

    if st.button("Start Speaking"):
        with st.spinner("Listening... Please start speaking.🎤"):
            recognized_text = recognize_speech_from_mic(language_code)
        
        # Clear the "Listening" message after recognition is done
        listening.empty()

        if recognized_text:
            st.markdown("<h3>Recognized Text 🖹 </h3>", unsafe_allow_html=True)
            st.text_area("Transcription", value=recognized_text, height=200, key="transcription", disabled=True)

            # Add recognized text to session state history
            st.session_state['history'].append(recognized_text)

            # Save transcription button
            if st.button("Save Transcription"):
                file_path = os.path.join(os.getcwd(), 'transcription.txt')
                with open(file_path, "a") as f:  # Append mode to save multiple transcriptions
                    f.write(f"{recognized_text}\n")
                st.success("Transcription saved successfully!")
        else:
            st.warning("No transcription available to save.")

# History Section with animated cards
st.markdown("<h3>Transcription History</h3>", unsafe_allow_html=True)
if st.session_state['history']:
    for item in st.session_state['history']:
        st.markdown(f"<div class='transcription-history'>{item}</div>", unsafe_allow_html=True)
else:
    st.markdown("<p>No history available yet.</p>", unsafe_allow_html=True)