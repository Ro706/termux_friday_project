import os
# Suppress pygame support message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import threading
import subprocess
from dotenv import load_dotenv

# Detect environment
IS_TERMUX = "TERMUX_VERSION" in os.environ

# Add subdirectories to path if necessary
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

# Import backend modules
from backend.Model import FirstLayerDMM
from backend.Chatbot import Chatbot
from backend.RealtimeSearchEngine import RealtimeInformation
from backend.Automation import (
    OpenApp, CloseApp, GoogleSearch, YouTubeSearch, 
    contentWrite, SystemCommand, VolumeControl, TakeScreenshot,
    CreateFolder
)
from backend.Features import ShowFeatures
from backend.ImageGeneration import GenerateImage
from backend.TextToSpeech import speak

# Import core modules
from core.news import news_report
from core.weather import tellmeTodaysWeather
from core.cpu_info import cpu_info
from core.ram_info import RamInfo
try:
    from core.PhotoCaptureApp import create_gui
except ImportError:
    create_gui = None
from core.mail import send_mail, send_whatsapp
from core.reminders import set_reminder

# Import game modules with error handling
games_available = True
try:
    import game1
    import game2
    import game3
    import game4
except ImportError:
    games_available = False

# Load environment variables
load_dotenv()
USERNAME = os.getenv("USERNAME", "User")

def handle_game_selection():
    """Handles interactive game selection when no game is specified."""
    if IS_TERMUX or not games_available:
        msg = "Games are currently not supported in this terminal environment."
        print(f"Friday: {msg}")
        speak(msg)
        return

    msg = "Which game would you like to play? 1. Tic Tac Toe, 2. Ball Bouncing, 3. Snake, 4. Rock Paper Scissors"
    print(f"Friday: {msg}")
    speak(msg)
    
    choice = input(f"[{USERNAME}]: ").strip().lower()
    if "1" in choice or "tic" in choice:
        speak("Starting Tic Tac Toe.")
        game1.game()
    elif "2" in choice or "ball" in choice:
        speak("Starting Ball Bouncing Game.")
        game2.start_game()
    elif "3" in choice or "snake" in choice:
        speak("Starting Snake Game.")
        game3.start_game()
    elif "4" in choice or "rock" in choice or "scissors" in choice or "paper" in choice:
        speak("Starting Rock Paper Scissors.")
        game4.start_game()
    else:
        err_msg = "Invalid selection. Please try again with a game name or number."
        print(f"Friday: {err_msg}")
        speak(err_msg)

def execute_task(task_query, original_prompt):
    """Executes a single task based on the classified query."""
    print(f"\n[Executing Task]: {task_query}")
    
    # Handle literal "(query)" or missing query text from Model.py
    def clean_query(prefix, text):
        q = text.replace(prefix, "").strip()
        if not q or q == "(query)":
            return original_prompt
        return q

    if task_query.startswith("general"):
        query = clean_query("general", task_query)
        response = Chatbot(query)
        print(f"Friday: {response}")
        speak(response)

    elif task_query.startswith("realtime"):
        query = clean_query("realtime", task_query)
        if "news" in query.lower():
            response = news_report()
            print(f"Friday: {response}")
        elif "weather" in query.lower():
            response = tellmeTodaysWeather()
            print(f"Friday: {response}")
        elif "cpu" in query.lower():
            response = cpu_info()
            print(f"Friday: {response}")
            speak(f"Here is your CPU information: {response}")
        elif "ram" in query.lower():
            response = RamInfo().info()
            print(f"Friday: {response}")
            speak(response)
        else:
            response = RealtimeInformation(query)
            print(f"Friday: {response}")
            speak(response)

    elif task_query.startswith("open"):
        app_name = clean_query("open", task_query)
        if "photo" in app_name.lower() or "camera" in app_name.lower():
            if IS_TERMUX:
                speak("Taking a photo using Termux camera.")
                timestamp = subprocess.check_output(["date", "+%Y%m%d_%H%M%S"]).decode().strip()
                filename = f"photo_{timestamp}.jpg"
                subprocess.run(["termux-camera-photo", filename])
                print(f"Photo saved as {filename}")
            elif create_gui:
                speak("Opening camera.")
                create_gui()
            else:
                speak("Camera application is not available.")
        elif "game" in app_name.lower():
            if IS_TERMUX or not games_available:
                speak("Games are not supported in this environment.")
            else:
                if "tic tac toe" in app_name.lower() or "1" in app_name.lower():
                    speak("Starting Tic Tac Toe.")
                    game1.game()
                elif "ball" in app_name.lower() or "2" in app_name.lower():
                    speak("Starting Ball Bouncing Game.")
                    game2.start_game()
                elif "snake" in app_name.lower() or "3" in app_name.lower():
                    speak("Starting Snake Game.")
                    game3.start_game()
                elif "rock" in app_name.lower() or "4" in app_name.lower():
                    speak("Starting Rock Paper Scissors.")
                    game4.start_game()
                else:
                    handle_game_selection()
        else:
            OpenApp(app_name)
            speak(f"Opening {app_name}.")

    elif task_query.startswith("close"):
        app_name = clean_query("close", task_query)
        CloseApp(app_name)
        speak(f"Closing {app_name}.")

    elif task_query.startswith("play"):
        song_name = clean_query("play", task_query)
        if "spotify" in song_name.lower():
            OpenApp("https://open.spotify.com/")
            speak("Opening Spotify.")
        else:
            YouTubeSearch(song_name)
            speak(f"Playing {song_name} on YouTube.")

    elif task_query.startswith("generate image"):
        prompt = clean_query("generate image", task_query)
        speak("Generating images, please wait.")
        GenerateImage(prompt)

    elif task_query.startswith("system"):
        cmd = clean_query("system", task_query)
        if cmd in ["mute", "unmute", "volume up", "volume down"]:
            VolumeControl(cmd)
        elif cmd in ["screenshot", "take screenshot"]:
            TakeScreenshot()
            speak("Screenshot taken.")
        elif cmd in ["features", "help", "menu"]:
            ShowFeatures()
            speak("Here are the features I can perform.")
        else:
            SystemCommand(cmd)

    elif task_query.startswith("content"):
        topic = clean_query("content", task_query)
        speak(f"Writing content about {topic}.")
        contentWrite(topic)

    elif task_query.startswith("google search"):
        topic = clean_query("google search", task_query)
        GoogleSearch(topic)
        speak(f"Searching Google for {topic}.")

    elif task_query.startswith("youtube search"):
        topic = clean_query("youtube search", task_query)
        YouTubeSearch(topic)
        speak(f"Searching YouTube for {topic}.")

    elif task_query.startswith("game"):
        game_name = clean_query("game", task_query)
        if IS_TERMUX or not games_available:
            speak("Games are not supported in this environment.")
        else:
            if "tic tac toe" in game_name or "1" in game_name:
                speak("Starting Tic Tac Toe.")
                game1.game()
            elif "ball" in game_name or "2" in game_name:
                speak("Starting Ball Bouncing Game.")
                game2.start_game()
            elif "snake" in game_name or "3" in game_name:
                speak("Starting Snake Game.")
                game3.start_game()
            elif "rock" in game_name or "4" in game_name:
                speak("Starting Rock Paper Scissors.")
                game4.start_game()
            else:
                handle_game_selection()

    elif task_query.startswith("mail"):
        speak("Preparing to send an email.")
        send_mail(original_prompt)

    elif task_query.startswith("whatsapp"):
        speak("Preparing to send a WhatsApp message.")
        send_whatsapp()

    elif task_query.startswith("reminder"):
        # Expecting something like "reminder 10 minutes (to) buy milk"
        clean_msg = clean_query("reminder", task_query)
        parts = clean_msg.split()
        if len(parts) >= 3:
            time_val = f"{parts[0]} {parts[1]}"
            rem_msg = " ".join(parts[2:])
            result = set_reminder(time_val, rem_msg)
            print(f"Friday: {result}")
            speak(result)
        else:
            speak("Please specify a time and a message for the reminder. For example, 5 minutes buy milk.")

    elif task_query.startswith("create folder"):
        folder_name = clean_query("create folder", task_query)
        result = CreateFolder(folder_name)
        # print(f"Friday: {result}") # result already has "Folder '...' created at ..."
        speak(result)

    elif task_query.startswith("knowledge"):
        topic = clean_query("knowledge", task_query)
        print(f"[bold blue][System]: Searching Knowledge Vault for: {topic}...[/bold blue]")
        speak("Searching your knowledge vault.")
        vault = KnowledgeVault()
        context = vault.get_relevant_context(topic)
        if context:
            response = Chatbot(topic, context=context)
        else:
            response = "I couldn't find any relevant information in your vault. Should I search the internet instead?"
        
        print(f"Friday: {response}")
        speak(response)

    elif task_query == "exit":
        speak("Goodbye! Have a nice day.")
        sys.exit()

def authenticate():
    """Simple password-based authentication for the assistant."""
    attempts = 3
    speak("Authentication required. Please enter your password.")
    
    while attempts > 0:
        password = input(f"\n[Security]: Enter Password ({attempts} attempts left): ").strip()
        
        if password == "rohit21":
            speak("Access granted. Welcome back, Rohit.")
            return True
        else:
            attempts -= 1
            if attempts > 0:
                msg = "Incorrect password. Please try again."
                print(f"Friday: {msg}")
                speak(msg)
            else:
                msg = "Too many failed attempts. Shutting down."
                print(f"Friday: {msg}")
                speak(msg)
                sys.exit()
    return False

def main():
    # Perform authentication first
    if not authenticate():
        return

    msg = f"Hello {USERNAME}, I am Friday. How can I help you today?"
    print(f"\n[Friday]: {msg}")
    speak(msg)

    try:
        while True:
            # Get Text Input
            query = input(f"\n[{USERNAME}]: ").strip()
            
            if not query:
                continue

            # Classify query
            tasks = FirstLayerDMM(query)
            
            # Execute tasks
            for task in tasks:
                execute_task(task, query)
    except KeyboardInterrupt:
        print("\n\n[Friday]: Detected Ctrl+C. Shutting down gracefully...")
        speak("Goodbye! Shutting down now.")
        sys.exit()
    except Exception as e:
        print(f"\n[Friday]: An unexpected error occurred: {e}")
        sys.exit()

if __name__ == "__main__":
    main()
