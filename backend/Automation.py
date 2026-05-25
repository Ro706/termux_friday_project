from webbrowser import open as webopen
try:
    import wikipedia
except ImportError:
    wikipedia = None
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import asyncio
import os
import sys

# Detect environment
IS_TERMUX = "TERMUX_VERSION" in os.environ

# Conditional imports
if not IS_TERMUX:
    try:
        from AppOpener import close, open as appopen
    except ImportError:
        appopen = close = None
    try:
        import keyboard
    except ImportError:
        keyboard = None
    try:
        import pyautogui
    except ImportError:
        pyautogui = None
    try:
        from pycaw.pycaw import AudioUtilities
    except ImportError:
        AudioUtilities = None
    try:
        from pywhatkit import playonyt, search
    except ImportError:
        playonyt = search = None
else:
    appopen = close = keyboard = pyautogui = AudioUtilities = playonyt = search = None

try:
    from TextToSpeech import speak
except ImportError:
    try:
        from backend.TextToSpeech import speak
    except ImportError:
        def speak(text): print(f"Friday: {text}")

# Load environment variables
env_vars = dotenv_values(".env")
GROQ_API_KEY = env_vars.get("GROQ_API_KEY", "").strip('"')
OPENWEATHER_API_KEY = env_vars.get("OPENWEATHER_API_KEY", "").strip('"')

# Instantiate Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

def GoogleSearch(query):
    print(f"[bold green]Searching Google for: {query}[/bold green]")
    if search:
        search(query)
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return query

def YouTubeSearch(query):
    print(f"[bold green]Searching YouTube for: {query}[/bold green]")
    if playonyt:
        playonyt(query)
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return query

def OpenWebsite(url):
    print(f"[bold green]Opening: {url}[/bold green]")
    webbrowser.open(url)
    return url

def CloseApp(app_name):
    print(f"[bold green]Closing: {app_name}[/bold green]")
    if IS_TERMUX:
        print("[yellow]Closing apps is not directly supported in Termux without root.[/yellow]")
    elif close:
        close(app_name)
    return app_name

def OpenApp(app_name):
    print(f"[bold green]Opening: {app_name}[/bold green]")
    
    # Common websites mapping
    websites = {
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "whatsapp": "https://web.whatsapp.com"
    }
    
    if app_name.lower() in websites:
        webbrowser.open(websites[app_name.lower()])
        return app_name

    if IS_TERMUX:
        # In Termux, we can try to open apps via 'am start' if we know the package name
        # but for now, we'll just search it or try termux-open
        print(f"[yellow]Attempting to open {app_name} via termux-open...[/yellow]")
        subprocess.run(["termux-open", f"https://www.google.com/search?q={app_name}"])
    elif appopen:
        try:
            appopen(app_name, match_closest=True)
        except Exception as e:
            print(f"AppOpener failed: {e}")
            webbrowser.open(f"https://www.google.com/search?q={app_name}")
    else:
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        
    return app_name

def contentWrite(query):
    if not groq_client:
        print("[bold red]Groq client not initialized.[/bold red]")
        return "Content generation unavailable."
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        result_content = response.choices[0].message.content.strip()

        if not result_content:
            print("[bold red]No content generated.[/bold red]")
            return "No content generated."

        print(result_content)
        filepath = os.path.abspath("content.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result_content)
        
        if IS_TERMUX:
            print(f"[bold green]Content saved to {filepath}[/bold green]")
        else:
            try:
                subprocess.Popen(["notepad.exe", filepath])
            except:
                pass

        return result_content

    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        return f"Error: {e}"


def TakeScreenshot(filename="screenshot.png"):
    try:
        filepath = os.path.abspath(filename)
        if IS_TERMUX:
            subprocess.run(["termux-screenshot", filepath])
        elif pyautogui:
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
        else:
            print("[bold red]Screenshot not supported on this platform/configuration.[/bold red]")
            return "Error: Unsupported"
            
        print(f"[bold green]Screenshot saved at {filepath}[/bold green]")
        return filepath
    except Exception as e:
        print(f"[bold red]Screenshot Error:[/bold red] {e}")
        return f"Error: {e}"

def GetWeather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            raise Exception(response.get("message", "Unknown error"))
        weather = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        result = f"Weather in {city}: {weather}, Temperature: {temp}°C"
        print(f"[bold blue]{result}[/bold blue]")
        speak(result)
        return result
    except Exception as e:
        print(f"[bold red]Weather Error:[/bold red] {e}")
        return f"Error: {e}"

def GetNews():
    try:
        rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        xml = requests.get(rss_url).text
        soup = BeautifulSoup(xml, "xml")
        headlines = [item.title.text for item in soup.find_all("item")[:5]]
        for i, h in enumerate(headlines, 1):
            print(f"[bold yellow]{i}. {h}[/bold yellow]")
            speak(h)
        return headlines
    except Exception as e:
        print(f"[bold red]News Error:[/bold red] {e}")
        return []

def TellJoke():
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?type=single").json()
        joke = response.get("joke", "Couldn't fetch a joke.")
        print(f"[italic green]Joke: {joke}[/italic green]")
        speak(joke)
        return joke
    except Exception as e:
        print(f"[bold red]Joke Error:[/bold red] {e}")
        return f"Error: {e}"

def WikiSummary(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        print(f"[bold magenta]Wikipedia Summary:[/bold magenta] {summary}")
        speak(summary)
        return summary
    except Exception as e:
        print(f"[bold red]Wikipedia Error:[/bold red] {e}")
        return f"Error: {e}"

def VolumeControl(action, step=10):
    try:
        if IS_TERMUX:
            # step is usually 0-100 for termux-volume
            # We first need to know which stream. Let's assume music.
            if action == "volume up":
                # This is a bit simplified; termux-volume needs absolute values
                # We'll just set it to a higher fixed value or use a relative increment if we had current volume
                subprocess.run(["termux-volume", "music", "70"]) 
                print("Volume Increased (Termux fixed to 70)")
            elif action == "volume down":
                subprocess.run(["termux-volume", "music", "30"])
                print("Volume Decreased (Termux fixed to 30)")
            elif action == "mute":
                subprocess.run(["termux-volume", "music", "0"])
                print("Muted")
        elif AudioUtilities:
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            current = volume.GetMasterVolumeLevelScalar()
            # step for scalar is 0.0 to 1.0
            win_step = step / 100.0
            if action == "volume up":
                volume.SetMasterVolumeLevelScalar(min(1.0, current + win_step), None)
            elif action == "volume down":
                volume.SetMasterVolumeLevelScalar(max(0.0, current - win_step), None)
            elif action == "mute":
                volume.SetMute(1, None)
            elif action == "unmute":
                volume.SetMute(0, None)
            print(f"Volume {action} executed.")
        else:
            print("Volume control not supported on this platform.")

    except Exception as e:
        print("Volume Control Error:", e)

def SystemCommand(cmd):
    cmd = cmd.lower()
    try:
        if IS_TERMUX:
            if "shutdown" in cmd or "power off" in cmd:
                print("[yellow]Shutdown requires root in Termux. Attempting 'poweroff'...[/yellow]")
                os.system("poweroff")
            elif "reboot" in cmd or "restart" in cmd:
                os.system("reboot")
            else:
                print(f"System command '{cmd}' not directly mapped for Termux.")
        else:
            if "shutdown" in cmd:
                os.system("shutdown /s /t 1")
            elif "restart" in cmd:
                os.system("shutdown /r /t 1")
            elif "sleep" in cmd:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif "log off" in cmd or "sign out" in cmd:
                os.system("shutdown /l")
        
        print(f"[bold green]Executed system command: {cmd}[/bold green]")
    except Exception as e:
        print(f"[bold red]System Command Error:[/bold red] {e}")

def CreateFolder(folder_name):
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            path = os.path.abspath(folder_name)
            print(f"[bold green]Folder created: {path}[/bold green]")
            return f"Folder '{folder_name}' created at {path}"
        else:
            path = os.path.abspath(folder_name)
            print(f"[bold yellow]Folder already exists: {path}[/bold yellow]")
            return f"Folder '{folder_name}' already exists at {path}"
    except Exception as e:
        print(f"[bold red]Create Folder Error:[/bold red] {e}")
        return f"Error creating folder: {e}"


# Example usage
if __name__ == "__main__":
    # content = contentWrite("write research paper for block chain and AI")
    # print(f"Chatbot: {content}")

    # Uncomment to try features:
    GoogleSearch("ChatGPT vs Gemini")
    # YouTubeSearch("AI in 2025")
    # GetWeather("Delhi")
    # GetNews()
    # TellJoke()
    # WikiSummary("Large Language Model")
    # SystemCommand("restart")
    # TakeScreenshot("test_screenshot.png")
    # SystemCommand("restart")
    # VolumeControl("increase")
    # VolumeControl("increase")
    # VolumeControl("increase")
    # VolumeControl("decrease")
    # VolumeControl("mute")
    # VolumeControl("unmute")