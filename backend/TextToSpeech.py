import subprocess
import threading
import queue
import time
import os

class TextToSpeech:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TextToSpeech, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.is_termux = "TERMUX_VERSION" in os.environ
        self.engine = None

        if not self.is_termux:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                selected_voice = voices[0].id
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        selected_voice = voice.id
                        break
                self.engine.setProperty('voice', selected_voice)
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 1.0)
            except Exception as e:
                print(f"Failed to initialize pyttsx3: {e}")
                self.engine = None
        
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        
        self._initialized = True

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                text = self.queue.get(timeout=0.1)
                if text:
                    if self.is_termux:
                        subprocess.run(["termux-tts-speak", text], capture_output=True)
                    elif self.engine:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    else:
                        print(f"TTS Output: {text}")
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS Worker Error: {e}")

    def speak(self, text):
        if text:
            self.queue.put(text)

_tts_engine = TextToSpeech()

def speak(text):
    _tts_engine.speak(text)

if __name__ == "__main__":
    speak("Testing the centralized text to speech system.")
    speak("This should handle multiple calls gracefully.")
    time.sleep(5)
