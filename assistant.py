from groq import Groq
import google.generativeai as googai
import json
import pyperclip
import cv2
from PIL import ImageGrab, Image

with open("API Keys.json") as file:
    keys = json.load(file)

groq_client = Groq(api_key=keys["Groq"])

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

def use_vision(prompt, photo_path):
    image = Image.ioen(photo_path)
    prompt = (
    "You are the vision analysis AI that extracts semantic meaning from images to provide context for another AI, which will respond to the user. "
    "Do not respond directly to the user. Instead, analyze the user-provided image and extract all relevant details and context based on the user's prompt. "
    f"Generate as much objective data about the image as possible for the AI assistant to use in crafting an appropriate response to the user. \nUSER PROMPT: {prompt}"
    )
    reply = goog_model.generate_content([prompt, image])
    return reply.text



def ask_llama(prompt):
    convo = [{'role': 'user', 'content': prompt}]
    completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    reply = completion.choices[0].message

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

webcam = cv2.VideoCapture(0)
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

prompt = input('User: ')
function_reply = call_function(prompt)
print(f'Function call: {function_reply}')
reply = ask_llama(prompt)
print(reply)