from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values
from backend.Database import AddMessage, GetMessages, ClearChatLog, InitDB

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Get the API key and username from environment variables
Username = env_vars.get("USERNAME", "").strip('"')
GroqAPIKey = env_vars.get("GROQ_API_KEY", "").strip('"')
Assistantname = "Friday"

# Initialize Database
InitDB()

# Initialize the Groq client
try:
    client = Groq(api_key=GroqAPIKey)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

# Define the initial system prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System},
]

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%I")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = (
        f'Please use this real-time information if needed,\n'
        f'Today is {day}, {date} {month} {year}.\n'
        f'The current time is {hour}:{minute}:{second}.\n'
    )
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def Chatbot(query, context=None):
    global client
    # List of supported models to try in order of preference
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
    
    try:
        if not client:
             client = Groq(api_key=GroqAPIKey)
        
        messages = GetMessages()
        
        # Prepare system prompt with optional context
        current_system = System
        if context:
            current_system += f"\n\n[CONTEXT FROM KNOWLEDGE VAULT]:\n{context}\n\nUsing the above context, answer the user's question accurately."

        system_messages = [{"role": "system", "content": current_system}, {"role": "system", "content": RealtimeInformation()}]
        combined_messages = system_messages + messages + [{"role": "user", "content": query}]

        completion = None
        for model_name in models:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=combined_messages,
                    max_completion_tokens=1024,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )
                # If we successfully start a stream, break the model loop
                if completion:
                    print(f"[System]: Using AI Model: {model_name}")
                    break
            except Exception as e:
                if "rate_limit_exceeded" in str(e).lower():
                    print(f"[Warning]: {model_name} rate limit reached. Trying fallback...")
                    continue
                else:
                    raise e

        if not completion:
            return "Error: All available AI models are currently busy or rate-limited. Please try again later."

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        AddMessage("user", query)
        AddMessage("assistant", Answer)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Chatbot Error: {e}")
        # ClearChatLog() # Optional: decide if you want to clear log on every error
        return f"I encountered an error while processing your request: {str(e)[:100]}..."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = Chatbot(user_input)
        print(f"Chatbot: {response}")
