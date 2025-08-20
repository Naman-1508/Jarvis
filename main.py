import webbrowser
import speech_recognition as sr
import pyttsx3
import time

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine = pyttsx3.init('sapi5')
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def processCommand(c):
    print("Processing command:", c)   # debug print
    c = c.lower()

    if "youtube" in c or "you tube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    elif any(word in c for word in ["leetcode", "leet code", "lead code", "lead coat", "lead cold"]):
        speak("Opening LeetCode")
        webbrowser.open("https://leetcode.com")
    elif "google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif "linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")
    elif "stop" in c or "exit" in c or "quit" in c:
        speak("Okay, shutting down. Goodbye sir!")
        exit(0)
    else:
        speak("Sorry, I didn't understand that.")

if __name__ == "__main__":
    speak("Initializing Jarvis...")

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

            command = recognizer.recognize_google(audio)
            if "jarvis" in command.lower():
                speak("Hi Sir! How can I help you?")
                time.sleep(1)
                # 🔄 continuous listening loop
                while True:
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=1)
                        print("Jarvis Activated...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

                    command = recognizer.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error:", e)
