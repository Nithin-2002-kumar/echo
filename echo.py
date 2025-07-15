import asyncio
import logging
import json
import pyttsx3
import speech_recognition as sr
import aiohttp
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import webbrowser

# Configuration
CONFIG_FILE = Path("echo_config.json")
LOG_FILE = Path("echo_assistant.log")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration data class"""
    name: str = "User"
    speech_rate: int = 170
    voice_id: int = 0
    hotword: str = "echo"
    wake_responses: List[str] = None
    weather_api_key: str = ""
    max_history: int = 100

    def __post_init__(self):
        if self.wake_responses is None:
            self.wake_responses = ["Yes?", "I'm here!", "How can I assist?"]

class EchoAI:
    def __init__(self):
        self.config = self.load_config()
        self.engine = self.init_speech_engine()
        self.recognizer = self.init_recognizer()
        self.history: List[Dict] = []
        self.running = True

    def load_config(self) -> Config:
        """Load configuration from JSON file"""
        try:
            if CONFIG_FILE.exists():
                with CONFIG_FILE.open('r') as f:
                    data = json.load(f)
                    return Config(**data)
            else:
                config = Config()
                self.save_config(config)
                return config
        except Exception as e:
            logger.error(f"Config load error: {str(e)}")
            return Config()

    def save_config(self, config: Config):
        """Save configuration to JSON file"""
        try:
            with CONFIG_FILE.open('w') as f:
                json.dump(config.__dict__, f, indent=2)
        except Exception as e:
            logger.error(f"Config save error: {str(e)}")

    def init_speech_engine(self) -> pyttsx3.Engine:
        """Initialize text-to-speech engine"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[self.config.voice_id].id)
            engine.setProperty('rate', self.config.speech_rate)
            return engine
        except Exception as e:
            logger.error(f"Speech engine init error: {str(e)}")
            raise

    def init_recognizer(self) -> sr.Recognizer:
        """Initialize speech recognizer"""
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        return recognizer

    async def speak(self, text: str, emotion: Optional[str] = None):
        """Convert text to speech with optional emotional inflection"""
        try:
            # Adjust speech parameters based on emotion
            original_rate = self.config.speech_rate
            volume = 0.9

            if emotion == "happy":
                self.engine.setProperty('rate', original_rate + 20)
                volume = 1.0
            elif emotion == "sad":
                self.engine.setProperty('rate', original_rate - 20)
                volume = 0.8

            self.engine.setProperty('volume', volume)
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Reset to default
            self.engine.setProperty('rate', original_rate)
            self.engine.setProperty('volume', 0.9)

            # Update history
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "assistant",
                "text": text,
                "emotion": emotion
            })
            if len(self.history) > self.config.max_history:
                self.history = self.history[-self.config.max_history:]

        except Exception as e:
            logger.error(f"Speak error: {str(e)}")

    async def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice commands with wake word detection"""
        with sr.Microphone() as source:
            try:
                logger.info("Listening for wake word...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio).lower()

                if self.config.hotword in text:
                    await self.speak(np.random.choice(self.config.wake_responses))
                    audio = self.recognizer.listen(source, timeout=10)
                    command = self.recognizer.recognize_google(audio).lower()
                    
                    self.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "speaker": "user",
                        "text": command,
                        "emotion": None
                    })
                    return command
                return None

            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except Exception as e:
                logger.error(f"Listen error: {str(e)}")
                return None

    async def process_command(self, command: str):
        """Process recognized commands"""
        try:
            command = command.lower().strip()
            if not command:
                return

            if "search" in command:
                await self.handle_search(command)
            elif "time" in command:
                await self.handle_time()
            elif "weather" in command:
                await self.handle_weather(command)
            elif "open" in command:
                await self.handle_open(command)
            elif any(word in command for word in ["exit", "quit", "goodbye"]):
                await self.shutdown()
            else:
                await self.speak("I'm not sure how to handle that command.")

        except Exception as e:
            logger.error(f"Command processing error: {str(e)}")
            await self.speak("Sorry, I encountered an error processing that command.")

    async def handle_search(self, command: str):
        """Handle search commands"""
        query = command.replace("search for", "").replace("search", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            await self.speak(f"Searching for {query}")
        else:
            await self.speak("What would you like me to search for?")

    async def handle_time(self):
        """Provide current time"""
        current_time = datetime.now().strftime("%I:%M %p")
        await self.speak(f"The current time is {current_time}")

    async def handle_weather(self, command: str):
        """Get weather information"""
        async with aiohttp.ClientSession() as session:
            try:
                # Simple location extraction (to be improved with NLP)
                location = command.replace("weather in", "").replace("weather", "").strip()
                if not location:
                    location = "New York"  # Default location

                if self.config.weather_api_key:
                    url = f"https://api.weatherapi.com/v1/current.json?key={self.config.weather_api_key}&q={location}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            temp = data["current"]["temp_c"]
                            condition = data["current"]["condition"]["text"]
                            await self.speak(f"The weather in {location} is {condition} with a temperature of {temp} degrees Celsius.")
                        else:
                            await self.speak(f"Sorry, I couldn't get the weather for {location}.")
                else:
                    await self.speak("Weather API key not configured.")
            except Exception as e:
                logger.error(f"Weather error: {str(e)}")
                await self.speak("I couldn't retrieve the weather information.")

    async def handle_open(self, command: str):
        """Handle application opening commands"""
        try:
            if "browser" in command:
                webbrowser.open("https://www.google.com")
                await self.speak("Opening web browser")
            elif "notepad" in command:
                import os
                os.system("notepad.exe")
                await self.speak("Opening Notepad")
            else:
                await self.speak("I can only open browser or notepad at the moment.")
        except Exception as e:
            logger.error(f"Open app error: {str(e)}")
            await self.speak("I couldn't open that application.")

    async def shutdown(self):
        """Clean shutdown"""
        await self.speak("Goodbye!")
        self.running = False

    async def run(self):
        """Main run loop"""
        await self.speak(f"Hello {self.config.name}, how can I assist you today?")
        
        while self.running:
            try:
                command = await self.listen()
                if command:
                    await self.process_command(command)
                await asyncio.sleep(0.1)  # Prevent CPU overload
            except Exception as e:
                logger.error(f"Main loop error: {str(e)}")
                await asyncio.sleep(1)

async def main():
    """Entry point"""
    assistant = EchoAI()
    await assistant.run()

if __name__ == "__main__":
    asyncio.run(main())
