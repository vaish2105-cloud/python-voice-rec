# Python AI Voice Assistant

A Python-based voice assistant that uses speech recognition to interpret spoken commands and automate common desktop and web tasks. It can launch supported applications, open websites, search Google, play YouTube videos, and provide weather, date, and time information.

## Features

- **Speech Recognition:** Converts spoken commands into text using Google Speech Recognition.
- **Voice Responses:** Uses `pyttsx3` to provide spoken responses.
- **Desktop Automation:** Launches supported applications such as Microsoft Word, Excel, PowerPoint, Chrome, VS Code, and Calculator.
- **Website Navigation:** Opens supported websites through voice commands.
- **Google Search:** Performs web searches based on spoken requests.
- **YouTube Playback:** Plays requested videos using PyWhatKit.
- **Weather Information:** Retrieves current weather information for a specified city through the OpenWeatherMap API.
- **Date and Time:** Announces the current date and time.
- **Multi-Command Processing:** Supports chaining multiple actions in one spoken command using connectors such as "then" and "after that."
- **Synonym Handling:** Uses NLTK WordNet to identify synonyms for selected action words.

## Technologies Used

- Python
- SpeechRecognition
- pyttsx3
- NLTK and WordNet
- PyWhatKit
- Requests
- OpenWeatherMap API

## Prerequisites

- Python installed on your computer
- A working microphone
- Internet connectivity for speech recognition, web searches, YouTube playback, and weather requests
- Supported desktop applications installed if you want to launch them

## Installation

Clone the repository:

```bash
git clone https://github.com/vaish2105-cloud/python-voice-rec.git
cd python-voice-rec
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure that the required Python packages are listed in `requirements.txt`.

## Configuration

Configure your OpenWeatherMap API key using an environment variable before running the application. Do not commit API keys or other credentials to GitHub.

## Run the Project

```bash
python voice_assistant.py
```

Speak a command when prompted. For example:

- "Open Chrome"
- "Search Python tutorials"
- "Play relaxing music"
- "What is the time?"
- "What's the weather?"

The exact commands supported depend on the application's command parsing and the applications installed on your system.

## Limitations

- Speech recognition depends on microphone quality, background noise, and internet connectivity.
- Application launching depends on the operating system and installed applications.
- Weather information requires a valid OpenWeatherMap API key.
- The assistant recognizes supported command patterns; it is not a general-purpose conversational AI system.

## Author

Vaishnavi Singh

GitHub: https://github.com/vaish2105-cloud
