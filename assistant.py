from groq import Groq
import google.generativeai as googai
from openai import OpenAI
from faster_whisper import WhisperModel
import speech_recognition as sr
import json
import pyperclip
import cv2
from PIL import ImageGrab, Image
import pyaudio
import os
import time
import re

with open("API Keys.json") as file:
    keys = json.load(file)

groq_client = Groq(api_key=keys["Groq"])

openai_client = OpenAI(api_key=keys["OpenAI"])

googai.configure(api_key=keys["Google"])
googai_config = {
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1, 
    'max_output_tokens':2048
}
googai_safety_config = [
    {
        'category': 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_NONE'
    }
]
goog_model = googai.GenerativeModel('gemini-1.5-flash-latest',
                                    generation_config=googai_config,
                                    safety_settings=googai_safety_config)

webcam = cv2.VideoCapture(0)

def use_vision(prompt, photo_path):
    image = Image.open(photo_path)
    prompt = (
    "You are the vision analysis AI that extracts semantic meaning from images to provide context for another AI, which will respond to the user. "
    "Do not respond directly to the user. Instead, analyze the user-provided image and extract all relevant details and context based on the user's prompt. "
    f"Generate as much objective data about the image as possible for the AI assistant to use in crafting an appropriate response to the user. \nUSER PROMPT: {prompt}"
    )
    reply = goog_model.generate_content([prompt, image])
    return reply.text

def ask_llama(prompt, image_context):
    if image_context:
        prompt = f'USER PROMPT: {prompt}\n\n    IMAGE CONTEXT: {image_context}'
    conversation.append({'role': 'user', 'content': prompt})
    completion = groq_client.chat.completions.create(messages=conversation, model='llama3-70b-8192')
    reply = completion.choices[0].message
    conversation.append(reply)

    return reply.content

def call_function(prompt):
    system_message = (
    "You are an AI function calling model. Determine whether to 'Extract Clipboard', 'Take Screenshot', 'Capture Webcam', or 'None' "
    "based on the user's prompt. Assume the webcam is a normal laptop webcam facing the user. "
    "Respond with only one selection from this list: ['Extract Clipboard', 'Take Screenshot', 'Capture Webcam', 'None']. "
    "Do not include any explanations. Format the function call name exactly as listed."
    )


    function_convo = [{'role': 'system', 'content': system_message},
                      {'role': 'user', 'content': prompt}]
    
    completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    reply = completion.choices[0].message

    return reply.content

def screenshot():
     ImageGrab.grab().convert('RGB').save(fp='screenshot.jpg', quality=15) #Take img, convert to RGB format, save to path at 15% quality for faster inference

def capture_webcam():
    if not webcam.isOpened():
        print('Error: Camera did not successfully open')
        exit()

    _, frame = webcam.read()
    cv2.imwrite(filename='webcam.jpg', img=frame)

def get_clipboard():
    content = pyperclip.paste()
    if isinstance(content, str):
        return content
    else:
        print('No clipboard text to copy.')
        return None

# Text-to-speech functionality
def speak(text):
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    stream_start = False

    with openai_client.audio.speech.with_streaming_response.create(
        model='tts-1',
        voice='onyx',
        response_format='pcm',
        input=text,
    ) as response:
        silence_threshold = 0.01
        for chunk in response.iter_bytes(chunk_size=1024):
            if stream_start:
                player_stream.write(chunk)
            else:
                if max(chunk) > silence_threshold:
                    player_stream.write(chunk)
                    stream_start = True

# Speech-to-text functionality
#cores = os.cpu_count() // 2
whisper_size = 'base'
stt_model = WhisperModel(
    whisper_size,
    device='cpu',
    compute_type='int8'
)

def wav_to_text(audio_path):
    segments, _ = stt_model.transcribe(audio_path)
    text = ''.join(segment.text for segment in segments)
    return text

wake_word = "Worko"

r = sr.Recognizer()
source = sr.Microphone()

def callback(recognizer, audio):
    prompt_audio_path = 'prompt.wav'
    with open(prompt_audio_path, 'wb') as f:
        f.write(audio.get_wav_data())

    prompt_text = wav_to_text(prompt_audio_path)
    clean_prompt = extract_prompt(prompt_text, wake_word)
    
    if clean_prompt:
        print(f"USER: {clean_prompt}")
        call = call_function(clean_prompt)

        if 'take screenshot' in call.lower():
            print('Taking Screenshot')
            screenshot()
            visual_context = use_vision(clean_prompt, 'screenshot.jpg')

        elif 'capture webcam' in call.lower():
            print('Capuring Webcam')
            capture_webcam()
            visual_context = use_vision(clean_prompt, 'webcam.jpg')
            webcam.release()

        elif 'extract clipboard' in call.lower():
            print('Copying Clipboard')
            context = get_clipboard()
            clean_prompt = f'{clean_prompt}\n\n CLIPBOARD CONTENT: {context}'
            visual_context = None

        else:
            visual_context = None
        
        reply = ask_llama(clean_prompt, visual_context)
        print(f"ASSISTANT: {reply}")
        speak(reply)

def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    print(f"\nSay", wake_word, f"followed by your prompt. \n")
    r.listen_in_background(source, callback) 
    
    while True:
        time.sleep(0.5)

def extract_prompt(transcribed_text, wake_word):
    pattern = rf"\b{re.escape(wake_word)}[\s,.?!]*([A-Za-z0-9].*)"
    match = re.search(pattern, transcribed_text, re.IGNORECASE)

    if match:
        prompt = match.group(1).strip()
        return prompt
    else:
        return None

system_message = (
    "You are a multimodal AI voice assistant. The user may or may not have attached a photo for context, which has been processed into a highly detailed text description. "
    "This description will accompany the transcribed voice prompt. Generate the most useful and factual response possible, carefully considering all previously generated text "
    "before adding new information. Do not request or expect images; use the context provided if available. Ensure your responses are relevant and useful in the conversation. "
    "Make your responses clear and concise, avoiding verbosity."
)

conversation = [{'role': 'system', 'content': system_message}]
       
start_listening()