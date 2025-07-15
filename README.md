EchoAI
EchoAI is a lightweight, modular voice assistant built in Python. It supports voice command recognition, text-to-speech responses, and basic task execution such as web searches, time queries, weather updates, and opening applications. Designed with an asynchronous architecture, EchoAI is efficient and extensible for personal or developmental use.
Features

Voice Interaction: Recognizes commands via a wake word ("echo" by default) and responds with natural text-to-speech.
Commands:
Check current time
Perform web searches
Retrieve weather information (requires API key)
Open applications (e.g., browser, notepad)


Asynchronous Design: Uses asyncio for non-blocking operation.
Configurable: Settings stored in a JSON file for easy customization.
Logging: Comprehensive logging to file and console for debugging.

Requirements

Python 3.8+
Dependencies (listed in requirements.txt):
pyttsx3: Text-to-speech engine
speechrecognition: Speech recognition
aiohttp: Asynchronous HTTP requests for weather API
numpy: Random response selection


A working microphone
Internet connection for weather and search features
(Optional) WeatherAPI key for weather functionality

Installation

Clone the Repository:
git clone https://github.com/your-username/echoai.git
cd echoai


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure the Assistant:

Copy echo_config.json.example to echo_config.json:cp echo_config.json.example echo_config.json


Edit echo_config.json to customize:
name: User name for personalized responses
speech_rate: Speech speed (default: 170)
voice_id: Voice selection (0 for male, 1 for female, depending on system)
hotword: Wake word (default: "echo")
weather_api_key: Obtain from WeatherAPI for weather features





Usage

Run the Assistant:
python EchoAI.py


Interact:

Say the wake word ("echo") followed by a command.
Example commands:
"Echo, what time is it?"
"Echo, search for Python tutorials"
"Echo, weather in London"
"Echo, open browser"
"Echo, goodbye" (to exit)




Logs:

Logs are saved to echo_assistant.log for debugging.



Configuration
The echo_config.json file allows customization:
{
  "name": "User",
  "speech_rate": 170,
  "voice_id": 0,
  "hotword": "echo",
  "wake_responses": ["Yes?", "I'm here!", "How can I assist?"],
  "weather_api_key": "",
  "max_history": 100
}


max_history: Limits stored conversation history to prevent memory issues.
wake_responses: List of responses to wake word activation.

Extending EchoAI
To add new commands:

Edit EchoAI.py and add a new method in the EchoAI class (e.g., async def handle_new_command(self, command)).
Update process_command to check for your command keywords and call the new method.
Test thoroughly and update this README with new features.

Troubleshooting

Microphone Issues: Ensure your microphone is properly connected and configured. Test with speech_recognition independently if needed.
Speech Recognition Errors: Check internet connectivity, as Google Speech Recognition is used by default.
Weather API Failures: Verify your WeatherAPI key in echo_config.json.
Logs: Check echo_assistant.log for detailed error messages.

Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a feature branch (git checkout -b feature/new-feature).
Commit changes (git commit -m "Add new feature").
Push to the branch (git push origin feature/new-feature).
Open a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Built with pyttsx3 for text-to-speech.
Uses SpeechRecognition for voice input.
Weather data powered by WeatherAPI.
