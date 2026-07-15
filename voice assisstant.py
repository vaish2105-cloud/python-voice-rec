import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import pywhatkit
import requests
import os
from nltk.corpus import wordnet as wn

# ---------------- TEXT TO SPEECH ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 175)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# ---------------- SPEECH TO TEXT ----------------
def take_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio).lower()
        print("You:", command)
        return command
    except:
        return ""


# ---------------- WORD MEANING AI (SYNONYMS) ----------------
def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word, pos=wn.VERB):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return synonyms

OPEN_WORDS = get_synonyms("open")
PLAY_WORDS = get_synonyms("play")
SEARCH_WORDS = get_synonyms("search")


# ---------------- SMART OPEN ----------------
APP_ALIASES = {

    # WORD
    "word": "winword",
    "ms word": "winword",
    "microsoft word": "winword",

    # EXCEL
    "excel": "excel",
    "ms excel": "excel",
    "microsoft excel": "excel",

    # POWERPOINT
    "powerpoint": "powerpnt",
    "ppt": "powerpnt",

    # TEAMS
    "teams": "ms-teams",
    "microsoft teams": "ms-teams",

    # FILE EXPLORER
    "file explorer": "explorer",
    "file manager": "explorer",
    "my files": "explorer",
    "explorer": "explorer",

    # BROWSER
    "chrome": "chrome",
    "google chrome": "chrome",

    # VS CODE
    "vscode": "code",
    "visual studio code": "code",

    # CALCULATOR
    "calculator": "calc",
    "calc": "calc"
}
def smart_open(target):

    target = target.lower()
    if target == "whatsapp":
        os.startfile("whatsapp:")
        speak("Opening WhatsApp")
        return
    # check alias
    if target in APP_ALIASES:
        real_name = APP_ALIASES[target]
        os.system(f"start {real_name}")
        speak(f"Opening {target}")
        return

    # websites
    websites = ["google", "youtube", "gmail", "instagram", "facebook", "chatgpt", "amazon", "netflix"]

    if target in websites:
        speak(f"Opening {target}")
        webbrowser.open(f"https://www.{target}.com")
        return

    # fallback
    os.system(f"start {target}")
    speak(f"Opening {target}")

# ---------------- WEATHER ----------------
def get_weather(city):
    api_key = "e3f9c8a313da01aa0ecce9a3978a0884"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        data = requests.get(url).json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        speak(f"The temperature in {city} is {temp} degree celsius with {desc}")
    except:
        speak("City not found")


# ---------------- PARSE HUMAN SENTENCE ----------------
def understand_command(sentence):

    connectors = [" then ", " and ", " after ", " after that "]

    parts = [sentence]

    # split into separate instructions
    for c in connectors:
        temp = []
        for p in parts:
            if c in p:
                temp.extend(p.split(c))
            else:
                temp.append(p)
        parts = temp

    tasks = []

    for part in parts:
        words = part.strip().split()

        for i, word in enumerate(words):

            if word in OPEN_WORDS:
                # EVERYTHING after open is target
                target = " ".join(words[i+1:])
                if target:
                    tasks.append(("open", target))
                break

            elif word in PLAY_WORDS:
                target = " ".join(words[i+1:])
                tasks.append(("play", target))
                break

            elif word in SEARCH_WORDS:
                target = " ".join(words[i+1:])
                tasks.append(("search", target))
                break

            elif "time" in word:
                tasks.append(("time", None))
                break

            elif "date" in word:
                tasks.append(("date", None))
                break

            elif "weather" in word:
                tasks.append(("weather", None))
                break

    return tasks

# ---------------- MAIN ----------------
def run_assistant():

    speak("Hello, I am your AI voice assistant")

    command = take_command()

    if command == "":
        speak("I did not hear anything")
        return

    tasks = understand_command(command)

    if not tasks:
        speak("Sorry, I did not understand")
        return

    for action, target in tasks:

        if action == "open":
            smart_open(target)

        elif action == "play":
            speak(f"Playing {target}")
            pywhatkit.playonyt(target)

        elif action == "search":
            speak(f"Searching {target}")
            webbrowser.open(f"https://www.google.com/search?q={target}")

        elif action == "time":
            speak(datetime.datetime.now().strftime("The time is %I:%M %p"))

        elif action == "date":
            speak(datetime.datetime.now().strftime("Today is %B %d %Y"))

        elif action == "weather":
            speak("Tell city name")
            city = take_command()
            get_weather(city)

    speak("Task completed")


run_assistant()
