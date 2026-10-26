import os
import re
import sys
import shutil
import subprocess
import webbrowser
import datetime
from pathlib import Path
from urllib.parse import urlencode
from difflib import get_close_matches

import requests
import speech_recognition as sr
import pyttsx3
import pywhatkit

# =========================================================
# 1. CONFIGURATION
# =========================================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv is not installed. Weather requires it.")

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty("rate", 175)

voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)


# =========================================================
# 2. TEXT-TO-SPEECH
# =========================================================

def speak(text):
    """Print a message and speak it aloud."""
    print("Assistant:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        # Keep a speech-engine problem from crashing the whole assistant.
        print("Text-to-speech error:", error)


# =========================================================
# 3. SPEECH RECOGNITION
# =========================================================

def take_command():
    """Listen through the microphone and return recognized text, or an empty string."""
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.9

    try:
        with sr.Microphone() as source:
            print("\nListening... Speak now.")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=12
            )

        print("Processing speech...")
        command = recognizer.recognize_google(audio).lower().strip()
        print("You:", command)
        return command

    except sr.WaitTimeoutError:
        print("No speech detected before the listening timeout.")
        return ""

    except sr.UnknownValueError:
        print("Speech was detected, but it could not be understood.")
        return ""

    except sr.RequestError as error:
        print("Speech recognition service error:", error)
        speak("Speech recognition is unavailable. Please check your internet connection.")
        return ""

    except (OSError, AttributeError) as error:
        print("Microphone error:", error)
        speak("Please check your microphone connection and Windows microphone permissions.")
        return ""


# =========================================================
# 4. DISCOVER WINDOWS APPLICATIONS
# =========================================================

def get_start_menu_folders():
    """Return common Windows Start Menu folders."""
    folders = []

    appdata = os.getenv("APPDATA")
    programdata = os.getenv("PROGRAMDATA")

    if appdata:
        folders.append(
            Path(appdata) / "Microsoft/Windows/Start Menu/Programs"
        )

    if programdata:
        folders.append(
            Path(programdata) / "Microsoft/Windows/Start Menu/Programs"
        )

    return folders


def discover_applications():
    """Find Windows application shortcuts in Start Menu folders."""
    apps = {}

    for folder in get_start_menu_folders():
        if not folder.exists():
            continue

        try:
            for shortcut in folder.rglob("*.lnk"):
                name = shortcut.stem.lower().strip()
                if name:
                    apps[name] = str(shortcut)
        except OSError as error:
            print("Could not scan Start Menu folder:", error)

    return apps


INSTALLED_APPS = discover_applications()


# =========================================================
# 5. APPLICATION ALIASES AND KNOWN APP COMMANDS
# =========================================================

APP_ALIASES = {
    "google chrome": "chrome",
    "chrome browser": "chrome",
    "microsoft edge": "edge",
    "edge browser": "edge",
    "ms word": "word",
    "microsoft word": "word",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "ppt": "powerpoint",
    "ms powerpoint": "powerpoint",
    "vscode": "visual studio code",
    "vs code": "visual studio code",
    "file manager": "file explorer",
    "my files": "file explorer",
    "calc": "calculator",
    "cmd": "command prompt",
    "my computer": "this pc",
}

# These commands are tried only if a Start Menu shortcut wasn't found.
APP_COMMANDS = {
    "chrome": ["chrome"],
    "edge": ["msedge"],
    "firefox": ["firefox"],
    "word": ["winword"],
    "excel": ["excel"],
    "powerpoint": ["powerpnt"],
    "visual studio code": ["code"],
    "notepad": ["notepad"],
    "calculator": ["calc"],
    "file explorer": ["explorer"],
    "command prompt": ["cmd"],
    "powershell": ["powershell"],
    "task manager": ["taskmgr"],
    "paint": ["mspaint"],
    "control panel": ["control"],
}

WEBSITES = {
    "google": "https://www.google.com/",
    "youtube": "https://www.youtube.com/",
    "gmail": "https://mail.google.com/",
    "instagram": "https://www.instagram.com/",
    "facebook": "https://www.facebook.com/",
    "chatgpt": "https://chatgpt.com/",
    "amazon": "https://www.amazon.in/",
    "netflix": "https://www.netflix.com/",
    "github": "https://github.com/",
    "linkedin": "https://www.linkedin.com/",
    "stackoverflow": "https://stackoverflow.com/",
    "wikipedia": "https://www.wikipedia.org/",
}


# =========================================================
# 6. FIND AND OPEN APPLICATIONS
# =========================================================

def normalize_name(name):
    """Normalize spaces and capitalization."""
    return re.sub(r"\s+", " ", name.lower().strip())


def resolve_app_name(target):
    """Find the closest supported or discovered application."""
    target = normalize_name(target)
    target = APP_ALIASES.get(target, target)

    if target in INSTALLED_APPS:
        return target

    if target in APP_COMMANDS:
        return target

    discovered_names = list(INSTALLED_APPS.keys())
    matches = get_close_matches(target, discovered_names, n=1, cutoff=0.72)
    if matches:
        return matches[0]

    matches = get_close_matches(
        target, list(APP_COMMANDS.keys()), n=1, cutoff=0.78
    )
    if matches:
        return matches[0]

    return None


def open_application(target):
    """Open a discovered or supported Windows application."""
    target = normalize_name(target)

    if target in {"settings", "windows settings"}:
        try:
            os.startfile("ms-settings:")
            speak("Opening Settings.")
        except OSError as error:
            print("Could not open Settings:", error)
            speak("I could not open Settings.")
        return

    if target in {"this pc", "my computer"}:
        try:
            os.startfile("explorer.exe")
            speak("Opening File Explorer.")
        except OSError as error:
            print("Could not open File Explorer:", error)
            speak("I could not open File Explorer.")
        return

    if target in {"whatsapp", "spotify"}:
        app_name = resolve_app_name(target)

        if app_name and app_name in INSTALLED_APPS:
            try:
                os.startfile(INSTALLED_APPS[app_name])
                speak(f"Opening {target}.")
                return
            except OSError as error:
                print("App shortcut launch failed:", error)

        urls = {
            "whatsapp": "https://web.whatsapp.com/",
            "spotify": "https://open.spotify.com/",
        }
        webbrowser.open(urls[target])
        speak(f"Opening {target} in your browser.")
        return

    app_name = resolve_app_name(target)
    if not app_name:
        speak(
            f"I could not find the application {target}. "
            "Say list applications to see discovered apps."
        )
        return

    shortcut = INSTALLED_APPS.get(app_name)
    if shortcut:
        try:
            os.startfile(shortcut)
            speak(f"Opening {app_name}.")
            return
        except OSError as error:
            print("Shortcut launch failed:", error)

    command = APP_COMMANDS.get(app_name)
    if command and shutil.which(command[0]):
        try:
            subprocess.Popen(command, shell=False)
            speak(f"Opening {app_name}.")
            return
        except OSError as error:
            print("Application launch failed:", error)

    speak(
        f"I found {app_name}, but could not launch it. "
        "Check whether it is installed."
    )


def list_applications():
    """Print discovered Start Menu application shortcuts."""
    names = sorted(INSTALLED_APPS.keys())

    if not names:
        speak("No Start Menu application shortcuts were found.")
        return

    print("\nDiscovered applications:")
    for name in names:
        print("-", name)

    speak(
        f"I found {len(names)} application shortcuts. "
        "Their names are printed in the terminal."
    )


# =========================================================
# 7. WEBSITES, GOOGLE SEARCH AND YOUTUBE
# =========================================================

def open_website(target):
    """Open a website from the supported list."""
    target = normalize_name(target)

    if target in WEBSITES:
        webbrowser.open(WEBSITES[target])
        speak(f"Opening {target}.")
    else:
        speak("That website is not in the supported list.")


def search_google(query):
    """Search Google using an encoded query."""
    query = query.strip()

    if not query:
        speak("Please tell me what you want to search for.")
        return

    url = "https://www.google.com/search?" + urlencode({"q": query})
    webbrowser.open(url)
    speak(f"Searching Google for {query}.")


def play_youtube(query):
    """Search for a video on YouTube using pywhatkit."""
    query = query.strip()

    if not query:
        speak("Please tell me what video you want to find.")
        return

    speak(f"Searching YouTube for {query}.")
    try:
        pywhatkit.playonyt(query)
    except Exception as error:
        print("YouTube playback error:", error)
        speak("I could not start YouTube. I will open the search results instead.")
        url = "https://www.youtube.com/results?" + urlencode({"search_query": query})
        webbrowser.open(url)


def search_youtube(query):
    """Open YouTube search results without automatically choosing a video."""
    query = query.strip()

    if not query:
        speak("Please tell me what you want to search for on YouTube.")
        return

    url = "https://www.youtube.com/results?" + urlencode({"search_query": query})
    webbrowser.open(url)
    speak(f"Showing YouTube search results for {query}.")


# =========================================================
# 8. WEATHER, DATE AND TIME
# =========================================================

def get_weather(city):
    """Retrieve current weather from OpenWeatherMap."""
    if not API_KEY:
        speak("Weather API key is not configured. Add it to your .env file.")
        return

    url = "https://api.openweathermap.org/data/2.5/weather"

    try:
        response = requests.get(
            url,
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]

        speak(
            f"The temperature in {city} is "
            f"{temperature} degrees Celsius, with {description}."
        )

    except requests.exceptions.HTTPError as error:
        print("Weather HTTP error:", error)
        speak("I could not retrieve the weather. Check the city name and API key.")
    except requests.exceptions.RequestException as error:
        print("Weather connection error:", error)
        speak("I could not connect to the weather service.")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        print("Weather response error:", error)
        speak("I could not read the weather information.")


def tell_time():
    """Speak the current local time."""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {current_time}.")


def tell_date():
    """Speak today's date."""
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today is {current_date}.")


# =========================================================
# 9. COMMAND PARSING
# =========================================================

def split_commands(sentence):
    """Split chained commands on phrases such as 'then' and 'after that'."""
    parts = re.split(
        r"\s+(?:and then|after that|then)\s+",
        sentence.lower()
    )
    return [part.strip() for part in parts if part.strip()]


def understand_command(sentence):
    """Convert recognized speech into action-target pairs."""
    sentence = normalize_name(sentence)
    tasks = []

    for part in split_commands(sentence):
        # Exit/help/list commands
        if part in {
            "exit", "quit", "goodbye", "stop assistant", "close assistant"
        }:
            tasks.append(("exit", None))
            continue

        # Do not require a special "help" command. Natural requests are welcome.
        if part in {"help", "what can you do", "commands"}:
            tasks.append(("help", None))
            continue

        if part in {
            "list applications", "show applications",
            "what applications are installed", "show installed applications"
        }:
            tasks.append(("list_apps", None))
            continue

        # Date and time
        if re.search(r"\btime\b", part):
            tasks.append(("time", None))
            continue

        if re.search(r"\bdate\b", part):
            tasks.append(("date", None))
            continue

        # Weather
        if re.search(r"\b(weather|temperature)\b", part):
            city_match = re.search(
                r"(?:weather|temperature)(?:\s+like)?(?:\s+in)?\s+(.+)$",
                part
            )
            city = city_match.group(1).strip() if city_match else ""

            if city in {"today", "now", "please"}:
                city = ""

            tasks.append(("weather", city or None))
            continue

        # Explicit YouTube search phrases
        youtube_search_match = re.match(
            r"^(?:search youtube for|search youtube|find a video for|"
            r"find videos for|look for a video about)\s+(.+)$",
            part
        )
        if youtube_search_match:
            tasks.append(("youtube_search", youtube_search_match.group(1).strip()))
            continue

        # "Open the best video for <topic>" should be a YouTube search,
        # not an attempt to launch a Windows application named after the topic.
        video_match = re.match(
            r"^(?:open|find|show)\s+(?:me\s+)?(?:the\s+)?"
            r"(?:best\s+)?(?:video|videos)\s+(?:for|about|on)\s+(.+)$",
            part
        )
        if video_match:
            tasks.append(("youtube_search", video_match.group(1).strip()))
            continue

        # Play/watch means try to start a video; if that fails, show search results.
        play_match = re.match(r"^(?:play|watch)\s+(.+)$", part)
        if play_match:
            tasks.append(("play", play_match.group(1).strip()))
            continue

        # Google search
        search_match = re.match(
            r"^(?:search(?:\s+google)?|google)\s+(?:for\s+)?(.+)$",
            part
        )
        if search_match:
            tasks.append(("search", search_match.group(1).strip()))
            continue

        if part.startswith("find "):
            tasks.append(("search", part[5:].strip()))
            continue

        # A single website name, such as "Google" or "YouTube", opens the website.
        # Check websites before applications so "Google" opens google.com,
        # rather than being treated as an application like Chrome.
        if part in WEBSITES:
            tasks.append(("website", part))
            continue

        # Opening a website or application
        open_match = re.match(r"^(?:open|go to|visit)\s+(.+)$", part)
        if open_match:
            target = open_match.group(1).strip()

            if target in WEBSITES:
                tasks.append(("website", target))
            else:
                tasks.append(("open_app", target))
            continue

    return tasks


# =========================================================
# 10. EXECUTE TASKS
# =========================================================

def execute_task(action, target):
    """Run one task. Return False when the assistant should exit."""
    if action == "open_app":
        open_application(target)

    elif action == "website":
        open_website(target)

    elif action == "search":
        search_google(target)

    elif action == "youtube_search":
        search_youtube(target)

    elif action == "play":
        play_youtube(target)

    elif action == "time":
        tell_time()

    elif action == "date":
        tell_date()

    elif action == "weather":
        city = target

        if not city:
            speak("Which city do you want the weather for?")
            city = take_command()

        if city:
            get_weather(city)
        else:
            speak("I did not hear a city name.")

    elif action == "list_apps":
        list_applications()

    elif action == "help":
        speak(
            "You can open applications or websites, search Google, "
            "search YouTube, play YouTube videos, check weather, ask for "
            "the date or time, or say list applications. "
            "For example, say search YouTube for Python tutorials."
        )

    elif action == "exit":
        return False

    return True


# =========================================================
# 11. CONTINUOUS ASSISTANT
# =========================================================

def run_assistant():
    """Listen continuously until an exit command is recognized."""
    speak(
        "Hello! I am your Python voice assistant. "
        "Tell me what you would like me to do."
    )

    while True:
        command = take_command()

        # A timeout or unclear phrase should not close the assistant.
        if not command:
            continue

        tasks = understand_command(command)

        if not tasks:
            speak(
                "I didn't understand that request. "
                "Please try saying what you would like me to do in another way."
            )
            continue

        should_continue = True

        for action, target in tasks:
            if not execute_task(action, target):
                should_continue = False
                break

        if not should_continue:
            speak("Goodbye!")
            break

        speak("Task completed.")


# =========================================================
# 12. START PROGRAM
# =========================================================

if __name__ == "__main__":
    try:
        if sys.platform != "win32":
            print("This assistant is designed primarily for Windows.")

        run_assistant()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
        speak("Assistant stopped.")
    except Exception as error:
        print("Unexpected assistant error:", error)
        speak("An unexpected error occurred. Check the terminal for details.")
