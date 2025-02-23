# 🎙️ Voice Typing for macOS

A free and customizable voice typing tool for macOS using OpenAI Whisper and GPT-3.5 Turbo. 🎤

🚀 **Transcribe speech into text** and **automatically type** it into any application with a simple hotkey!

## ✨ Features
✅ **Hotkey Activation** – Start/Stop recording with `Page Down`
✅ **AI-Powered Transcription** – Uses OpenAI Whisper for speech-to-text
✅ **Punctuation & Grammar Fixes** – GPT-3.5 Turbo refines output
✅ **Customizable** – Modify settings and tweak behavior as needed
✅ **Free & Open Source** – No subscriptions, full control over your data

## 📦 Installation

### 1️⃣ Install Dependencies
Ensure you have Python 3.10+ installed. Then, run:

```sh
pip install -r requirements.txt
```

### 2️⃣ Set Up OpenAI API Key
Create a `.env` file in the project root and add:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

### 3️⃣ Run the Script
```sh
python voice_typing.py
```

## 🛠️ Configuration
You can adjust settings like:
- **Whisper Model Size** (default: `small`)
- **Hotkeys**
- **Output Formatting**

Modify these inside `voice_typing.py`.

## 🖥️ How It Works
1️⃣ Press `Page Down` to start recording.
2️⃣ Speak naturally – the script captures your voice.
3️⃣ Release `Page Down` – the AI transcribes and types the text for you.

## ❓ Troubleshooting
- **MacBook M1/M2 Users:** Ensure `torch` is installed with MPS support.
- **Slow Transcription?** Try a smaller Whisper model (`tiny`, `base`).
- **Permission Issues?** Enable microphone access in macOS settings.

## 🤝 Contributing
Pull requests are welcome! Open an issue for suggestions or bugs.

## 📜 License
This project is licensed under the MIT License.

---

💡 **Enjoy effortless voice typing on macOS!** 🚀
