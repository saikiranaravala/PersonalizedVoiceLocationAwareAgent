"""Speech recognition and text-to-speech services."""

import speech_recognition as sr
import pyttsx3

from utils.config import config
from utils.logger import logger


class SpeechService:
    """Service for speech recognition and text-to-speech."""

    def __init__(self):
        """Initialize speech service."""
        self.recognizer = sr.Recognizer()
        self.language = config.get("speech.language", "en-US")
        
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', config.get("speech.rate", 150))
            self.tts_engine.setProperty('volume', config.get("speech.volume", 0.9))
            logger.info("Text-to-speech engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Listen for voice input and convert to text.

        Args:
            timeout: Maximum time to wait for speech to start (seconds)
            phrase_time_limit: Maximum time for phrase (seconds)

        Returns:
            Recognized text or empty string if failed
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening for voice input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("Processing speech...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.warning("No speech detected within timeout")
            return ""
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return ""

    def speak(self, text: str) -> bool:
        """Convert text to speech and play it.

        Args:
            text: Text to convert to speech

        Returns:
            True if successful, False otherwise
        """
        if not text:
            logger.warning("No text provided for speech synthesis")
            return False
            
        if not self.tts_engine:
            logger.error("TTS engine not available")
            print(f"Assistant: {text}")  # Fallback to console output
            return False

        try:
            logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Error during text-to-speech: {e}")
            print(f"Assistant: {text}")  # Fallback to console output
            return False

    def is_microphone_available(self) -> bool:
        """Check if microphone is available.

        Returns:
            True if microphone is accessible, False otherwise
        """
        try:
            with sr.Microphone() as source:
                return True
        except Exception as e:
            logger.error(f"Microphone not available: {e}")
            return False

    def test_microphone(self) -> bool:
        """Test microphone and speech recognition.

        Returns:
            True if test successful, False otherwise
        """
        try:
            logger.info("Testing microphone and speech recognition...")
            self.speak("Please say something to test the microphone.")
            
            with sr.Microphone() as source:
                logger.info("Speak now...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Microphone test successful. Recognized: {text}")
                self.speak(f"I heard: {text}")
                return True
                
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False
