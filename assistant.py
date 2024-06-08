from groq import Groq
import json
import pyperclip
import cv2
from PIL import ImageGrab

with open("API Keys.json") as file:
    keys = json.load(file)

groq_client = Groq(api_key=keys["Groq"])

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

### Function Options
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