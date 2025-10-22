#!/usr/bin/env python3
"""
Roger - Fully Offline AI Assistant
----------------------------------
✅ No API keys
✅ No internet needed (except for opening YouTube or sites)
✅ Works on Windows / macOS / Linux
✅ Voice-controlled
✅ Completely free

Wake word: "roger"
"""

import os
import sys
import json
import queue
import time
import webbrowser
import subprocess
import threading
from datetime import datetime

import pyttsx3
import wikipedia
import pywhatkit
import pyaudio
from vosk import Model, KaldiRecognizer

# ---------------------------
# SETTINGS
# ---------------------------
WAKE_WORDS = ["roger", "hey roger", "ok roger"]
MODEL_PATH = "model/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
# ---------------------------

# Initialize text-to-speech engine
tts = pyttsx3.init()
tts.setProperty("rate", 170)
tts.setProperty("volume", 1.0)

def say(text):
    """Speak + print text."""
    print(f"Roger: {text}")
    thread = threading.Thread(target=lambda: [tts.say(text), tts.runAndWait()])
    thread.start()

# Check offline model
if not os.path.exists(MODEL_PATH):
    say("Offline model not found. Please download it first.")
    print("Download from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
    print("Extract to folder: model/vosk-model-small-en-us-0.15/")
    sys.exit(1)

# Load Vosk offline model
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
audio_q = queue.Queue()

# Start PyAudio microphone
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
                input=True, frames_per_buffer=8192)
stream.start_stream()

def mic_listener():
    """Continuously listen and push recognized text into a queue."""
    while Tr
