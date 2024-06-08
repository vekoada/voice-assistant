from groq import Groq
import json

with open("API Keys.json") as file:
    keys = json.load(file)

groq_client = Groq(api_key=keys["Groq"])

def ask_llama(prompt):
    convo = [{'role': 'user', 'content': prompt}]
    completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    reply = completion.choices[0].message

    return reply.content

