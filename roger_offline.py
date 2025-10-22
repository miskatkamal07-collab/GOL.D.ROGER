#!/usr/bin/env python3
"""
Roger - Fully Offline AI Assistant
----------------------------------
✅ No API keys
✅ No internet needed for speech recognition (only for opening websites / YouTube)
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
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if result.get("text"):
                audio_q.put(result["text"])

listener_thread = threading.Thread(target=mic_listener, daemon=True)
listener_thread.start()

def listen_for_text(timeout=6):
    """Wait for recognized speech (timeout in seconds)."""
    try:
        return audio_q.get(timeout=timeout)
    except queue.Empty:
        return ""

def remove_wakeword(text):
    """Remove wake word if present."""
    for w in WAKE_WORDS:
        if w in text:
            return text.replace(w, "").strip()
    return text

def tell_time():
    now = datetime.now().strftime("%I:%M %p")
    say(f"The time is {now}")

def open_site(site):
    if not site.startswith("http"):
        site = "https://www." + site
    webbrowser.open(site)
    say(f"Opening {site}")

def play_youtube(song):
    say(f"Playing {song} on YouTube")
    pywhatkit.playonyt(song)

def wiki_search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        say(result)
    except Exception:
        say("I couldn't find that on Wikipedia.")

def run_cmd(cmd):
    say(f"Running command {cmd}")
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        say(out[:150])
    except Exception:
        say("Command failed.")

def handle_command(cmd):
    cmd = cmd.strip()
    if not cmd:
        return

    if "time" in cmd:
        tell_time()
    elif cmd.startswith("open "):
        open_site(cmd[5:])
    elif cmd.startswith("play "):
        play_youtube(cmd[5:])
    elif "wikipedia" in cmd:
        wiki_search(cmd.replace("wikipedia", "").strip())
    elif cmd.startswith("run "):
        run_cmd(cmd[4:])
    elif cmd in ["stop", "exit", "quit"]:
        say("Goodbye.")
        sys.exit(0)
    else:
        say("Sorry, I can’t do that yet.")

def main():
    say("Roger is online and listening. Say 'Roger' to wake me up.")
    while True:
        text = listen_for_text(timeout=5)
        if not text:
            continue
        print("Heard:", text)
        if any(w in text for w in WAKE_WORDS):
            say("Yes?")
            command = listen_for_text(timeout=7)
            if command:
                print("Command:", command)
                handle_command(remove_wakeword(command))
            else:
                say("I didn’t catch that.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        say("Roger signing off.")
        sys.exit(0)

