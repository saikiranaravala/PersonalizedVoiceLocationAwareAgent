"""
services/speech.py  —  Safe speech wrapper for headless server deployment
==========================================================================
On Render (and any headless Linux server), pyaudio / pyttsx3 / SpeechRecognition
are not available. This module guards every import so the server starts cleanly.

Speech recognition and synthesis are handled client-side by the browser's
Web Speech API. This module is only relevant for local desktop runs.
"""

import os
from utils.logger import logger

# ── Feature flags ─────────────────────────────────────────────────────────────
# Set ENABLE_LOCAL_SPEECH=true in your local .env to enable hardware audio.
# On Render, leave it unset (defaults to False).
_LOCAL_SPEECH_ENABLED = os.environ.get("ENABLE_LOCAL_SPEECH", "false").lower() == "true"

# ── Conditional imports ───────────────────────────────────────────────────────
_sr   = None   # SpeechRecognition
_tts  = None   # pyttsx3

if _LOCAL_SPEECH_ENABLED:
    try:
        import speech_recognition as _sr
        logger.info("SpeechRecognition loaded (local mode)")
    except ImportError:
        logger.warning("SpeechRecognition not available — mic input disabled")

    try:
        import pyttsx3 as _tts
        logger.info("pyttsx3 loaded (local mode)")
    except ImportError:
        logger.warning("pyttsx3 not available — local TTS disabled")
else:
    logger.info("Local speech disabled (headless/server mode). Browser handles STT/TTS.")


# ── Public API ────────────────────────────────────────────────────────────────

def is_speech_available() -> bool:
    """Returns True only when running locally with audio hardware."""
    return _LOCAL_SPEECH_ENABLED and _sr is not None


def listen_from_microphone(timeout: int = 5) -> str:
    """
    Capture speech from microphone and return transcript.
    Returns empty string on server / when unavailable.
    """
    if not is_speech_available():
        logger.debug("listen_from_microphone called on headless server — skipped")
        return ""

    try:
        recognizer = _sr.Recognizer()
        with _sr.Microphone() as source:
            logger.info("Listening from microphone...")
            audio = recognizer.listen(source, timeout=timeout)
        text = recognizer.recognize_google(audio)
        logger.info(f"Recognized: {text}")
        return text
    except Exception as e:
        logger.warning(f"Speech recognition error: {e}")
        return ""


def speak_text(text: str) -> None:
    """
    Speak text via local TTS engine.
    No-op on server / when unavailable (browser handles TTS).
    """
    if not _LOCAL_SPEECH_ENABLED or _tts is None:
        logger.debug("speak_text called on headless server — skipped")
        return

    try:
        engine = _tts.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.warning(f"TTS error: {e}")
