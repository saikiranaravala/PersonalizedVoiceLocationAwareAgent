"""Speech recognition and synthesis service.

On Render (headless server), pyaudio / pyttsx3 / SpeechRecognition are not
available — and not needed. The browser handles STT/TTS via the Web Speech API.
This module guards every hardware import so the server starts cleanly while
preserving the full SpeechService API so nothing else needs changing.

To enable local mic/speaker on a dev machine, set in your .env:
    ENABLE_LOCAL_SPEECH=true
"""

import os
import threading
from typing import Callable, Optional

from utils.config import config
from utils.logger import logger

# ── Detect environment ────────────────────────────────────────────────────────
_LOCAL_SPEECH_ENABLED = os.environ.get("ENABLE_LOCAL_SPEECH", "false").lower() == "true"

# ── Conditional imports — never crash on headless servers ─────────────────────
_sr = None
_pyttsx3 = None

if _LOCAL_SPEECH_ENABLED:
    try:
        import speech_recognition as _sr
        logger.info("SpeechRecognition loaded (local mode)")
    except ImportError:
        logger.warning("SpeechRecognition not installed — mic input disabled")

    try:
        import pyttsx3 as _pyttsx3
        logger.info("pyttsx3 loaded (local mode)")
    except ImportError:
        logger.warning("pyttsx3 not installed — local TTS disabled")
else:
    logger.info("Local speech disabled (headless/server mode). Browser handles STT/TTS.")


class SpeechService:
    """Service for speech recognition and synthesis.

    On a headless server all methods are safe no-ops.
    On a local machine with ENABLE_LOCAL_SPEECH=true, full hardware audio works.
    """

    def __init__(self):
        """Initialize speech service."""
        self.is_listening = False
        self.is_speaking = False

        # Only initialise hardware objects when libraries are present
        self.recognizer = _sr.Recognizer()  if _sr      else None
        self.microphone = _sr.Microphone()  if _sr      else None
        self.tts_engine = _pyttsx3.init()   if _pyttsx3 else None

        if self.tts_engine:
            self._setup_tts()

        if self.microphone:
            self._adjust_for_ambient_noise()

        if not _LOCAL_SPEECH_ENABLED:
            logger.info("SpeechService running in server mode (no-op stubs active)")

    # ── Private helpers ───────────────────────────────────────────────────────

    def _setup_tts(self):
        """Configure text-to-speech settings."""
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            rate   = config.get("speech.tts_rate",  180)
            volume = config.get("speech.tts_volume", 0.9)
            self.tts_engine.setProperty('rate',   rate)
            self.tts_engine.setProperty('volume', volume)
            logger.info("TTS engine configured")
        except Exception as e:
            logger.warning(f"TTS setup error (non-fatal): {e}")

    def _adjust_for_ambient_noise(self):
        """Adjust microphone for ambient noise."""
        try:
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Ambient noise adjustment complete")
        except Exception as e:
            logger.warning(f"Could not adjust for ambient noise (non-fatal): {e}")

    # ── Public API — all methods safe to call on server ───────────────────────

    def listen(self, timeout: int = None, phrase_time_limit: int = None) -> Optional[str]:
        """Listen for speech and return transcript.
        Returns None immediately on a headless server (browser handles STT).
        """
        if not self.recognizer or not self.microphone:
            logger.debug("listen() called on headless server — skipped")
            return None

        try:
            timeout           = timeout           or config.get("speech.listen_timeout",    10)
            phrase_time_limit = phrase_time_limit or config.get("speech.phrase_time_limit", 15)

            with self.microphone as source:
                self.is_listening = True
                logger.info("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
                self.is_listening = False

            logger.info("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text

        except Exception as e:
            logger.warning(f"Speech recognition error: {e}")
            self.is_listening = False
            return None

    def speak(self, text: str, blocking: bool = True) -> None:
        """Convert text to speech.
        No-op on a headless server (browser handles TTS).
        """
        if not text:
            return
        if not self.tts_engine:
            logger.debug(f"speak() called on headless server — skipped: {text[:60]}")
            return

        try:
            self.is_speaking = True
            logger.info(f"Speaking: {text[:50]}...")
            if blocking:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                thread = threading.Thread(target=self._speak_async, args=(text,), daemon=True)
                thread.start()
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            if blocking:
                self.is_speaking = False

    def _speak_async(self, text: str) -> None:
        """Async speech helper."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Async TTS error: {e}")
        finally:
            self.is_speaking = False

    def stop_speaking(self) -> None:
        """Stop current speech."""
        if not self.tts_engine:
            return
        try:
            self.tts_engine.stop()
            self.is_speaking = False
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")

    def listen_and_respond(
        self,
        process_callback: Callable[[str], str],
        timeout: int = None,
    ) -> Optional[str]:
        """Listen for input, process it, and speak the response."""
        user_input = self.listen(timeout=timeout)
        if user_input:
            response = process_callback(user_input)
            if response:
                self.speak(response)
            return user_input
        return None
