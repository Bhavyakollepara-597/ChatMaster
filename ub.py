import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import google.generativeai as genai
from gtts import gTTS
import base64
from googletrans import Translator




os.environ['FLASK_ENV'] = 'development'

app = Flask(__name__,template_folder='template',static_url_path='/static')

CORS(app)
app.debug = True


GEMINI_API_KEY = "AIzaSyCqUr6nqXj2xq1Ol4LaVSZDkERBoV9j4U0"


# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

text_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize Translator
translator = Translator()
@app.route('/patience.html')
def patience():
   return render_template('patience.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    target_language = data.get('target_language')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    response_message = sendMessage(user_message,target_language)
    return jsonify({"response": response_message})

# def sendMessage(message):
#     try:
#         if message.lower().startswith('translate'):
#             _, text, target_language = message.split(' ', 2)
#             response_message = translate_text(text, target_language)
#         elif message.lower().startswith('weather'):
#             _, city = message.split('in', 1)
#             response_message = getWeather(city.strip())
        
#         else:
#             response_message = get_text_response(message)
            
#         return response_message
#     except Exception as e:
#         return f"Error: {str(e)}"
def sendMessage(message, target_language):
    try:
        if target_language and target_language != 'en':
            translated_message = translate_text(message, target_language)
            response_message = get_text_response(translated_message, target_language)
        else:
            response_message = get_gemini_response(message)
        return response_message
    except Exception as e:
        return f"Error: {str(e)}"

def get_gemini_response(question):
    try:
        response = text_model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [question],
                }
            ]
        ).send_message(question)
        response_text = ''.join(chunk.text for chunk in response if chunk.text)
        return response_text
    except Exception as e:
        return f"An error occurred: {e}"

def getWeather(city):
    response = requests.get(
        f'https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}'
    )
    if response.status_code == 200:
        data = response.json()
        print(data)
        if 'current' in data:
            if 'temp_c' in data['current'] and 'condition' in data['current']:
                temperature = data['current']['temp_c']
                condition = data['current']['condition']['text']
                return f"The weather in {city} is {temperature}°C with {condition}."
            else:
                return "Error: Missing temperature or condition data in the response."
        else:
            return "Error: 'current' key not found in the response."
    else:
        return f"Error: Failed to fetch weather data. Status code: {response.status_code}"


    

def get_text_response(question, target_language='en'):
    try:
        if not question.strip():  # Check if the question is empty or contains only whitespace
            return "Please provide a valid question."

        detected_lang = detect_language(question)
        translated_question = translate_text(question,  target_language='en')
        response = text_model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        question,
                    ],
                }
            ]
        ).send_message(question)
        response_text = ''.join(chunk.text for chunk in response if chunk.text)
        
        return response_text
    except Exception as e:
        return f"An error occurred: {e}"

def detect_language(text):
    try:
        detected_lang = translator.detect(text)
        return detected_lang
    except Exception as e:
        return 'en'
def translate_text(text, target_language):
    try:
        if text is None:
            return "No text to translate"
        
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def generate_voice(text, language='en'):
    tts = gTTS(text, lang=language_code(language))
    tts.save("response.mp3")
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    return audio_base64

def language_code(language_name):
    language_codes = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "Hindi": "hi",
        "Telugu": "te",
        "Chinese (Simplified)": "zh-CN",
        "Arabic": "ar",
        "Bengali": "bn",
        "Russian": "ru",
        "Portuguese": "pt",
        "Japanese": "ja",
        
    }
    return language_codes.get(language_name, "en")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
