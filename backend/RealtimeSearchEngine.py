import requests
from bs4 import BeautifulSoup
from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import load_dotenv
from backend.Database import AddMessage, GetMessages, ClearChatLog, InitDB

# Load environment variables from .env file
load_dotenv()

# Get the API key and username from environment variables
Username = os.getenv("USERNAME", "")
GroqAPIKey = os.getenv("GROQ_API_KEY", "")
Assistantname = "Friday"  # Define the assistant name

# Initialize Database
InitDB()

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide answers in a professional way, make sure to add full stops, commas, question marks, and use proper grammar. ***
*** Just answer the question from the provided data in a professional way. ***
"""

# DuckDuckGo search function (replaces the unreliable google-search)
def GoogleSearch(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.select('.result__body')
        
        Answer = f"The search results for '{query}' are:\n[Start]\n"
        count = 0
        for res in results:
            if count >= 5:
                break
            title = res.select_one('.result__title').text.strip() if res.select_one('.result__title') else "No Title"
            snippet = res.select_one('.result__snippet').text.strip() if res.select_one('.result__snippet') else "No Snippet"
            Answer += f"Title: {title}\nDescription: {snippet}\n\n"
            count += 1
        
        Answer += "[End]"
        return Answer
    except Exception as e:
        print(f"Search Error: {e}")
        return f"The search for '{query}' failed to return results."

# Answer formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# System ChatBot prompt
BaseSystemChat = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Real-time information
def Information():
    current_date_time = datetime.datetime.now()
    return (
        f'Use this real-time information if needed:\n'
        f'Day: {current_date_time.strftime("%A")}\n'
        f'Date: {current_date_time.strftime("%d")}\n'
        f'Month: {current_date_time.strftime("%B")}\n'
        f'Year: {current_date_time.strftime("%Y")}\n'
        f'Time: {current_date_time.strftime("%I")} hours, '
        f'{current_date_time.strftime("%M")} minutes, '
        f'{current_date_time.strftime("%S")} seconds\n'
    )

# Main chatbot function
def RealtimeInformation(prompt):
    # Load chat history from Database
    messages = GetMessages()

    # Dynamic system prompt with Google search
    system_chat_dynamic = BaseSystemChat + [
        {"role": "system", "content": GoogleSearch(prompt)},
        {"role": "system", "content": Information()}
    ]

    # Generate completion
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=system_chat_dynamic + messages + [{"role": "user", "content": prompt}],
        max_completion_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    
    # Save updated chat history to Database
    AddMessage("user", prompt)
    AddMessage("assistant", Answer)

    return AnswerModifier(Answer)

# CLI
if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = RealtimeInformation(user_input)
        print(f"Chatbot: {response}")

# CLI
if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        response = RealtimeInformation(user_input)
        print(f"Chatbot: {response}")
