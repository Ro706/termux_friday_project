import cohere
from rich import print
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
cohere_api_key = os.getenv("COHERE_API_KEY")

# Check if the API key is set
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY is not set in the .env file")

# Initialize the Cohere client
co = cohere.Client(cohere_api_key)

# Define the list of functions
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "mail", "game", "create folder"
]

# ... (preamble)
"""
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general (query)' if a query can be answered by a language model (conversational AI chatbot) and doesn't require any up-to-date information. Examples:
...
-> Respond with 'mail' if a query is asking to send an email or open the mail tool. Examples:
  - Query: "Send an email."
    Response: "mail"
  - Query: "I want to send a mail."
    Response: "mail"

-> Respond with 'game (game name)' if a query is asking to play a game. Examples:
  - Query: "I want to play a game."
    Response: "game"
  - Query: "Play Tic Tac Toe."
    Response: "game tic tac toe"
"""

# Initialize the messages list
messages = []

# Define the preamble for the model
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general (query)' if a query can be answered by a language model (conversational AI chatbot) and doesn't require any up-to-date information. Examples:
  - Query: "Who was Akbar?"
    Response: "general Who was Akbar?"
  - Query: "How can I study more effectively?"
    Response: "general How can I study more effectively?"
  - Query: "What is Python programming language?"
    Response: "general What is Python programming language?"
  - Query: "What's the time?"
    Response: "general What's the time?"
  - Query: "Tell me a joke."
    Response: "general Tell me a joke."

-> Respond with 'realtime (query)' if a query cannot be answered by a language model (because they don't have real-time data) and requires up-to-date information. Examples:
  - Query: "Who is the Indian Prime Minister?"
    Response: "realtime Who is the Indian Prime Minister?"
  - Query: "Tell me about Facebook's recent update."
    Response: "realtime Tell me about Facebook's recent update."
  - Query: "Tell me news about coronavirus."
    Response: "realtime Tell me news about coronavirus."
  - Query: "What is today's news?"
    Response: "realtime What is today's news?"
  - Query: "What is the current weather in Delhi?"
    Response: "realtime What is the current weather in Delhi?"
  - Query: "What is the AQI of Nagpur?"
    Response: "realtime What is the AQI of Nagpur?"
  - Query: "What is the net worth of Elon Musk?"
    Response: "realtime What is the net worth of Elon Musk?"

-> Respond with 'open (application name or website name)' if a query is asking to open any application or website. Examples:
  - Query: "Open Facebook."
    Response: "open Facebook"
  - Query: "Open Telegram."
    Response: "open Telegram"

-> Respond with 'close (application name)' if a query is asking to close any application or website. Examples:
  - Query: "Close Notepad."
    Response: "close Notepad"
  - Query: "Close Facebook."
    Response: "close Facebook"

-> Respond with 'play (song name)' if a query is asking to play any song. Examples:
  - Query: "Play Afsanay by YS."
    Response: "play Afsanay by YS"
  - Query: "Play Let Her Go."
    Response: "play Let Her Go"

-> Respond with 'generate image (image prompt)' if a query is requesting to generate an image with a given prompt. Examples:
  - Query: "Generate image of a lion."
    Response: "generate image of a lion"
  - Query: "Generate image of a cat."
    Response: "generate image of a cat"

-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder. Examples:
  - Query: "Set a reminder at 9:00 PM on 25th June for my business meeting."
    Response: "reminder 9:00 PM 25th June business meeting"

-> Respond with 'system (task name)' if a query is asking to perform system tasks like mute, unmute, volume up, volume down, shutdown, restart, sleep, features, help, menu, etc. Examples:
  - Query: "Mute the volume."
    Response: "system mute"
  - Query: "Increase the volume."
    Response: "system volume up"
  - Query: "Shutdown the system."
    Response: "system shutdown"
  - Query: "Restart my computer."
    Response: "system restart"
  - Query: "Put the system to sleep."
    Response: "system sleep"
  - Query: "Show me the feature list."
    Response: "system features"
  - Query: "What can you do?"
    Response: "system help"
  - Query: "Open the menu."
    Response: "system menu"

-> Respond with 'content (topic)' if a query is asking to write any type of content like applications, codes, emails, or anything else about a specific topic. Examples:
  - Query: "Write an email to my boss."
    Response: "content email to boss"
  - Query: "Write a Python script to sort a list."
    Response: "content Python script to sort a list"

-> Respond with 'google search (topic)' if a query is asking to search a specific topic on Google. Examples:
  - Query: "Search for Python tutorials."
    Response: "google search Python tutorials"

-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on YouTube. Examples:
  - Query: "Search for Python tutorials on YouTube."
    Response: "youtube search Python tutorials"

-> Respond with 'mail' if a query is asking to send an email or open the mail tool. Examples:
  - Query: "Send an email."
    Response: "mail"

-> Respond with 'game (game name)' if a query is asking to play a game. Examples:
  - Query: "Play a game."
    Response: "game"
  - Query: "Play Tic Tac Toe."
    Response: "game tic tac toe"
  - Query: "I want to play Snake."
    Response: "game snake"
  - Query: "Play Rock Paper Scissors."
    Response: "game rock paper scissors"

-> Respond with 'create folder (folder name)' if a query is asking to create a new folder. Examples:
  - Query: "Create a folder named raj."
    Response: "create folder raj"
  - Query: "Make a new folder called photos."
    Response: "create folder photos"

*** If the query is asking to perform multiple tasks like 'open Facebook, Telegram and close WhatsApp', respond with 'open Facebook, open Telegram, close WhatsApp'. ***
*** If the user is saying goodbye or wants to end the conversation like 'bye Friday.', respond with 'exit'. ***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define the chat history
CharHistory = [
    {"role": "User", "message": "Hello, how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "Do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "Open Chrome and tell me about Mahatma Gandhi."},
    {"role": "Chatbot", "message": "open Chrome, general tell me about Mahatma Gandhi."},
    {"role": "User", "message": "Open Edge and open Chrome."},
    {"role": "Chatbot", "message": "open Edge, open Chrome."},
    {"role": "User", "message": "What is today's date and by the way remind me that I have a dancing performance."},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00 PM 5th Aug dancing performance."},
    {"role": "User", "message": "Chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "Tell me a joke."},
    {"role": "Chatbot", "message": "general tell me a joke."},
    {"role": "User", "message": "What is the AQI of Nagpur?"},
    {"role": "Chatbot", "message": "realtime what is the AQI of Nagpur?"},
    {"role": "User", "message": "What is the net worth of Elon Musk?"},
    {"role": "Chatbot", "message": "realtime what is the net worth of Elon Musk?"},
    {"role": "User", "message": "Generate image of a lion."},
    {"role": "Chatbot", "message": "generate image of a lion"},
    {"role": "User", "message": "Set a reminder at 9:00 PM on 25th June for my business meeting."},
    {"role": "Chatbot", "message": "reminder 9:00 PM 25th June business meeting"},
    {"role": "User", "message": "Mute the volume."},
    {"role": "Chatbot", "message": "system mute"}
]

def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "User", "message": prompt})

    # Combine preamble and user query
    full_prompt = f"{preamble}\nUser: {prompt}\nChatbot:"

    try:
        response = co.chat(
            model="command-r-08-2024",
            message=prompt,
            preamble=preamble,
            temperature=0.3,
            max_tokens=50
        )
    except Exception as e:
        print(f"[ERROR] Cohere API call failed: {e}")
        return ["error"]

    generated_text = response.text.strip()
    print(f"Generated Text: {generated_text}")

    # Normalize and split responses
    response_list = [i.strip().lower() for i in generated_text.split(",")]

    valid_responses = []
    for task in response_list:
        for func in funcs:
            if task.startswith(func):
                valid_responses.append(task)
                break

    # Fallback to general if nothing matched
    if not valid_responses:
        return [f"general {prompt.lower()}"]

    return valid_responses



if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(FirstLayerDMM(user_input))
