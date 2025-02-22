import pyaudio
import wave
import os
import openai
import threading
import time
import wave
from dotenv import load_dotenv
from pynput import keyboard
from pynput.keyboard import Controller

# Load environment variables from .env file
load_dotenv()

# 🔑 OpenAI API Key (Use environment variables for security)
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("❌ ERROR: OpenAI API key not found! Make sure you have a .env file with OPENAI_API_KEY.")
    exit(1)

# 🎙️ Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "voice_input.wav"

# 🔄 State variables
is_recording = False
recording_start_time = None
audio = pyaudio.PyAudio()
stream = None
frames = []
recording_thread = None
keyboard_controller = Controller()  # 💻 Keyboard controller for typing

def record_audio():
    """Captures audio chunks while recording is active."""
    global is_recording, stream, frames
    while is_recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

def start_recording():
    """Starts recording audio."""
    global is_recording, stream, frames, recording_thread, recording_start_time
    if is_recording:
        return

    print("🎤 Recording started... Press PgDown again to stop.")
    is_recording = True
    recording_start_time = time.time()  # Start time
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

def stop_recording():
    """Stops recording and saves the file."""
    global is_recording, stream, frames, recording_thread, recording_start_time
    if not is_recording:
        return None

    is_recording = False
    recording_thread.join()  
    stream.stop_stream()
    stream.close()

    duration = time.time() - recording_start_time
    if duration < 0.1:
        print("❌ Recording too short! Ignoring.")
        return None

    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"✅ Audio saved as {OUTPUT_FILENAME}")
    return OUTPUT_FILENAME

def transcribe_audio(audio_file):
    # Ensure the file exists and isn't empty
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        print("⚠️ No valid audio file found.")
        return ""

    # Check if the audio file is too short by measuring duration
    try:
        with wave.open(audio_file, "rb") as wf:
            duration = wf.getnframes() / float(wf.getframerate())
            if duration < 0.1:
                print(f"⚠️ Audio too short ({duration:.3f}s), not transcribing.")
                return ""
    except Exception as e:
        print(f"⚠️ Error reading audio file: {e}")
        return ""

    # Proceed with transcription
    with open(audio_file, "rb") as f:
        response = openai.Audio.transcribe("whisper-1", f)

    return response["text"]

def improve_punctuation(text):
    """Uses ChatGPT to add proper punctuation to the transcribed text."""
    # If text already has punctuation, assume it's correct
    if any(p in text for p in ['.', '!', '?', ',']):
        return text

    print("✨ Improving punctuation...")
    chat_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that adds proper punctuation to transcriptions."},
            {"role": "user", "content": f"Please punctuate the following transcription correctly:\n\n{text}"}
        ]
    )

    return chat_response["choices"][0]["message"]["content"]

def type_text(text):
    """Simulates keyboard typing of transcribed text into any application."""
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

            # Improve punctuation if necessary
            text = improve_punctuation(text)
            print(f"✍️ Final Text: {text}")

            type_text(text)  # 💻 Type transcribed text into active window

# 🚀 Start keyboard listener
print("🎙️ Voice typing ready! Press Page Down to record.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
