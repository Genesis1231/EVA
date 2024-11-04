# E.V.A. 🎙️

<div align="center">

![EVA Logo](logo.png)

*Experimental Voice Assistant*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/Genesis1231/EVA)](https://github.com/Genesis1231/EVA/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Genesis1231/EVA)](https://github.com/Genesis1231/EVA/stargazers)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## 🎯 Overview of EVA

Hello Github wizards! Thanks for stopping by~ 🤗

So, here's the story - I used to sling code back in the days (like, when Perl was still cool), but then a year ago AI came along and stroke me with awe. I became very interested in human-AI interaction and how it can be applied in our daily life. However, most of the online projects only focused on a few specific tasks. So I spent a few months to develop EVA myself. 

EVA is an experimental voice assistant that explores human-AI experience through proactive engagement and autonomous behavior. Built with a modular architecture, it aims to provide a more natural and dynamic interaction to users, include an extensive tool framework that allows for continuous enhancement of its capabilities.

<div align="center">
  <img src="path/to/demo.gif" alt="EVA Demo" width="600px"/>
</div>


## ✨ Key Features

EVA is built on LangGraph framework, with some customized modules and tools. Importantly, You can run it purely local with no cost. (if you have a GPU computer)

### 🎙️ Cross platform modular design
- Configurable model selection for LLM, TTS, STT, etc.
- Integrated with OpenAI, Anthropic, Groq, Google, and Ollama.
- Easy modification of prompts and tools.
- Supports both desktop and mobile app

### 🖼️ Interactive experience
- Voice ID and vision ID for personalized interaction.
- Proactive style communication (varies between models)
- Multi-modal outputs with asynchronous action.

### 🔌 Dynamic Tool system
- Web search through DuckDuckGo/Tavily
- Youtube video search
- Discord Midjourney AI image generation
- Suno music generation
- Screenshot and analysis 
- Compatible with all Langchain tools
- Easy implementation of new tool with single file.


## 📁 Project Structure

```
EVA/
├── app/
│   ├── client/          # Client-side implementation
│   ├── config/          # Configuration files and log
│   ├── core/            # Core process
│   ├── data/            # Data storage
│   ├── tools/           # Tool implementations
│   └── utils/           # Utility functions
│       ├── agent/       # LLM agent classes and functions
│       ├── memory/      # Mmeory module classes 
│       ├── prompt/      # Utility prompts
│       ├── stt/         # Speech recognition models and classes
│       ├── tts/         # Text-to-Speech models and classes
│       └── vision/      # Vision models and functions
├── tests/               # Test cases (😢)
└── docs/                # Documentation (😩)

```

## 🚀 Setup Guide


### 💻System Requirements

- Python 3.10+
- CUDA-compatible GPU (if you want to run locally)

### 📥 Quick Start

Clone repository
```bash
git clone https://github.com/Genesis1231/EVA.git
cd EVA
```

Create virtual environment
```bash
python3 -m venv eva_env
source eva_env/bin/activate  
```

Install dependencies
```bash
pip install -r requirements.txt
pip install git+https://github.com/wenet-e2e/wespeaker.git
```

Configure .env with your API keys
```bash
cp .env.example .env
```

Run EVA 
```bash
cd app
python main.py
```
Similarly, you can run EVA with docker.

```dockerfile
# Use official Python image with FastAPI
FROM tiangolo/uvicorn-gunicorn-fastapi

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsndfile1 \
    ffmpeg \

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

```

### 🛠️ Configuration
configure EVA setting in app/config/config.py 

```python
eva_configuration = {
    "DEVICE": "desktop", # Currently "desktop" or "mobile" (testing)
    "LANGUAGE": "en", # Only english for now, need to have prompt templates in other languages.
    "BASE_URL": "http://localhost:11434", # URL for local Ollama server, you can leave it if you dont plan to use local models
    "CHAT_MODEL": "anthropic", # Supports Anthropic-Claude3.5, Groq-llama3.1-70b, OpenAI-ChatGPT-4o, Mistral Large, Google Gemini 1.5 Pro, and Ollama models, Recommend: Claude or Chatgpt 
    "IMAGE_MODEL": "openai", # Supports Chatgpt-4o-mini and Ollama llava-phi3/llava13b(local), recommend: 4omini, but llava-phi3 is very small and free. 
    "STT_MODEL": "faster-whisper", # supports OpenAI Whisper, Groq(free) and Faster-whisper(local).  
    "TTS_MODEL": "elevenlabs", # Supports elevenlabs, openAI and coqui TTS (local).
    "SUMMARIZE_MODEL": "llama" # Supports groq-llama3.1-8b, Anthropic-claude-sonnet3.5 and Ollama-llama3.1(local).
}
```

The best combination(my preference):
- Claude3.5/Chatgpt-4o as the chat model. The response is more coherent with larger amount of input information.
- Chatgpt-4o-mini as the image model, because of accuracy and low cost.
- Faster-whisper as the STT model. since this local approach is actually 2x faster than all online models.
- Elevenlabs as the TTS model, for the best quality.

EVA also works with a completely free combination:
- Ollama-llama3.1-70b as the chat model. (if you have a good GPU, you can also use groq-llama3.2)
- Ollama-llava-phi3 as the image model.
- Faster-whisper as the speech recognition model.
- Coqui TTS as the TTS model.

The performance is also good if you have a decent GPU. 
Groq is free too but it has a limit for token usage per minute. So you might run out of tokens quickly.


### 🔧 Tool Setup

- Music generation tool Requires a Suno-API docker running on the base_url. 
  Install from https://github.com/gcui-art/suno-api

- Image generation tool requires a midjourney account and a private discord server.
  Need include the discord channel information in .env file.

If you want to disable some tools, just change the client setting in related .py file.

```python
    client: str = "none"
```
But I like to leave them all on since it is very interesting to observe how AI select tools.


## 🤝 Contribution

Due to my limited time, the code is far from perfect. I would be very grateful if anyone is willing to contribute🍝


## 📜 License

This project is licensed under the MIT License.


## 📊 Credits & Acknowledgments

This project wouldn't be possible without these amazing open-source projects:

### Core & Language Models
- [LangChain](https://github.com/langchain-ai/) - Amazing AI Dev Framework 
- [Groq](https://github.com/groq/) - Free LLM access and really fast
- [Ollama](https://github.com/ollama/) - Best local model deployment
- [Numpy](https://github.com/numpy/) - The Numpy
- [FastAPI](https://github.com/fastapi/) - Excellent API framework
- [Tqdm](https://github.com/tqdm/) - Great progress bar

### Utility modules
- [OpenCV](https://github.com/opencv/) - Legendary Vision Library
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Fastest Speech transcription
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Admirable text-to-speech synthesis
- [Face Recognition](https://github.com/ageitgey/face_recognition) - Face detection
- [Speech Recognition](https://github.com/Uberi/speech_recognition) - Easy-to-use Speech detection
- [PyAudio](https://github.com/jleb/pyaudio) - Powerful Audio I/O 
- [Wespeaker](https://github.com/wenet-e2e/wespeaker) - Speaker verification
- [NLTK](https://github.com/nltk/) - Natural Language Toolkit

### Tools development
- [Chromium](https://github.com/chromium/) - Best open-source web browser
- [DuckDuckGo](https://github.com/duckduckgo/) - Free Web search
- [Youtube_search](https://github.com/joetats/youtube_search) - YouTube search
- [Suno-API](https://github.com/suno-ai/suno-api) - Music generation API for Suno
- [PyautoGUI](https://github.com/asweigart/pyautogui) - cross-platform GUI automation


<div align="center">
  <sub>Built with ❤️ by the Adam</sub>
</div>
