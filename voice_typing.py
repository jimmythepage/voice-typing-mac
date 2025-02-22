import pyaudio
import wave
import os
import openai
import threading
import time
from dotenv import load_dotenv
from pynput import keyboard
from pynput.keyboard import Controller

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("❌ ERROR: OpenAI API key not found! Make sure you have a .env file with OPENAI_API_KEY.")
    exit(1)

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "voice_input.wav"

# State variables
is_recording = False
audio = pyaudio.PyAudio()
stream = None
frames = []
recording_thread = None
keyboard_controller = Controller()

def record_audio():
    """Captures audio while recording is active."""
    global is_recording, stream, frames
    while is_recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

def start_recording():
    """Starts recording audio."""
    global is_recording, stream, frames, recording_thread
    if is_recording:
        return

    print("🎤 Recording started... Press PgDown again to stop.")
    is_recording = True
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

def stop_recording():
    """Stops recording and saves the file."""
    global is_recording, stream, frames, recording_thread
    if not is_recording:
        return None

    is_recording = False
    recording_thread.join()
    stream.stop_stream()
    stream.close()

    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"✅ Audio saved as {OUTPUT_FILENAME}")
    return OUTPUT_FILENAME

def transcribe_audio(audio_file):
    """Transcribes audio using OpenAI Whisper."""
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print("⚠️ No valid audio file found.")
        return ""

    with open(audio_file, "rb") as f:
        response = openai.Audio.transcribe("whisper-1", f)

    return response["text"]

def improve_punctuation(text):
    """Uses GPT-3.5-turbo for punctuation improvement."""
    if not text.strip():
        return text

    print("✨ Improving punctuation (using GPT-3.5)...")
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that adds proper punctuation to transcriptions."},
            {"role": "user", "content": f"Please punctuate the following transcription correctly:\n\n{text}"}
        ]
    )

    return chat_response["choices"][0]["message"]["content"]

def type_text(text):
    """Simulates keyboard typing of transcribed text."""
    print(f"⌨️ Typing: {text}")
    keyboard_controller.type(text)

def on_press(key):
    """Handles key press event to start recording."""
    global is_recording
    if key == keyboard.Key.page_down and not is_recording:
        start_recording()

def on_release(key):
    """Handles key release event to stop recording and type text."""
    if key == keyboard.Key.page_down:
        print("🛑 Stopping recording...")
        audio_file = stop_recording()
        if audio_file:
            print("📄 Transcribing...")
            text = transcribe_audio(audio_file)
            print(f"📝 Transcribed (Raw): {text}")

            text = improve_punctuation(text)  # Punctuation correction
            print(f"✍️ Final Text: {text}")

            type_text(text)

# Start keyboard listener
print("🎙️ Voice typing ready! Press Page Down to record.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
