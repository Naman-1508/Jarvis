import webbrowser
import speech_recognition as sr
import win32com.client
import time
import requests
import wikipedia
from dotenv import load_dotenv
import os
import datetime
import pywhatkit as kit
import difflib
import sys

# Load environment variables
load_dotenv()

recognizer = sr.Recognizer()
speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Voice = speaker.GetVoices().Item(1)  # Mark voice
speaker.Rate = 3
speaker.Volume = 100

def speak(text):
    try:
        speaker.Speak(text)
    except Exception as e:
        print("🔊 Error in speak():", e)

# ------------------ AI Chat ------------------
def chat_with_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.1", "prompt": prompt}
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        result = ""
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if '"response":"' in data:
                    part = data.split('"response":"')[1].split('"')[0]
                    result += part
        return result.strip()
    except Exception as e:
        print("⚡ Error talking to Ollama:", e)
        return None

# ------------------ Weather ------------------
def get_weather(command):
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            speak("API key missing.")
            return
        words = command.split()
        if "in" in words:
            city_index = words.index("in") + 1
            if city_index < len(words):
                city = " ".join(words[city_index:])
            else:
                speak("Say city after 'in'.")
                return
        else:
            speak("Say weather in <city>.")
            return
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        data = requests.get(url, timeout=5).json()
        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("Could not fetch weather.")
    except:
        speak("Something went wrong fetching weather.")

# ------------------ Command Processor ------------------
def processCommand(c):
    try:
        c = c.lower()
        command_map = {
            "open youtube": lambda: (speak("Opening YouTube"), os.system("start youtube:")),
            "open github": lambda: (speak("Opening GitHub"),os.system("start https://github.com")),
            "open google": lambda: (speak("Opening Google"), os.system("start https://google.com")),
            "open linkedin": lambda: (speak("Opening LinkedIn"), os.system("start https://linkedin.com")),
            "open leetcode": lambda: (speak("Opening LeetCode"), os.system("start https://leetcode.com")),
            "open notepad": lambda: os.system("notepad.exe"),
            "open calculator": lambda: os.system("calc.exe"),
            "open command prompt": lambda: os.system("start cmd"),
            "open paint": lambda: os.system("mspaint"),
            "open word": lambda: os.system("start winword"),
            "open excel": lambda: os.system("start excel"),
            "open powerpoint": lambda: os.system("start powerpnt"),
            "open settings": lambda: os.system("start ms-settings:"),
            "open control panel": lambda: os.system("control"),
        }

        if any(word in c for word in ["weather", "wether", "whether"]):
            get_weather(c)
        elif "who is" in c or "what is" in c:
            query = c.replace("who is","").replace("what is","")
            try:
                result = wikipedia.summary(query, sentences=2)
                speak(result)
            except:
                speak("Could not find on Wikipedia.")
        elif "time" in c:
            speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
        elif "date" in c:
            speak(f"Today is {datetime.date.today().strftime('%B %d, %Y')}")
        elif "play" in c:
            song = c.replace("play","").strip()
            speak(f"Playing {song} on YouTube")
            kit.playonyt(song)
        elif any(word in c for word in ["stop","exit","quit"]):
            speak("Goodbye sir!")
            sys.exit(0)
        else:
            closest_match = difflib.get_close_matches(c, command_map.keys(), n=1, cutoff=0.6)
            if closest_match:
                command_map[closest_match[0]]()
            else:
                response = chat_with_ollama(c)
                if response:
                    speak(response)
                else:
                    speak("Sorry, I couldn't process that.")
    except Exception as e:
        print("⚠️ Error:", e)

# ------------------ Main Loop ------------------
if __name__ == "__main__":
    speak("System online. Listening for wake word 'Jarvis'.")
    last_activity = time.time()
    auto_shutdown = 300  # 5 minutes

    IDLE = True  # waiting for wake word

    while True:
        try:
            # 1️⃣ Auto shutdown check
            if time.time() - last_activity > auto_shutdown:
                speak("No activity detected. Shutting down. Goodbye sir!")
                sys.exit(0)

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                heard = ""
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=4)
                    heard = recognizer.recognize_google(audio).lower()
                except:
                    heard = ""

                if IDLE:
                    # 2️⃣ Wake word detection
                    if "jarvis" in heard:
                        speak("Yes sir, I am listening.")
                        IDLE = False
                        last_activity = time.time()
                else:
                    # 3️⃣ ACTIVE state: listen for actual command once
                    with sr.Microphone() as cmd_source:
                        recognizer.adjust_for_ambient_noise(cmd_source, duration=0.5)
                        try:
                            audio_cmd = recognizer.listen(cmd_source, timeout=10, phrase_time_limit=15)
                            command = recognizer.recognize_google(audio_cmd).lower()
                            print(f"Command: {command}")
                            processCommand(command)
                        except:
                            speak("I didn't catch that.")
                    # 4️⃣ Return to IDLE state after processing command
                    IDLE = True
                    last_activity = time.time()

        except KeyboardInterrupt:
            speak("Shutting down manually. Goodbye sir!")
            sys.exit(0)
