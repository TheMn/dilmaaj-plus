# Farsi to English AI Dubbing Tool

A lightweight, free, and fully offline AI tool that automatically dubs Farsi (Persian) `.mp3` audio files into English.

It uses **OpenAI Whisper** to translate the Farsi speech to English while capturing precise timestamps, **Piper TTS** to generate a natural-sounding offline English voice, and **FFmpeg/Pydub** to stretch or compress the generated speech so it aligns perfectly with the original speaker's pauses and rhythm.

## Features
- **100% Free & Offline**: Uses local models, meaning no paid APIs or internet connection is required after the initial setup.
- **Timestamp Synchronization**: The English audio speed is dynamically adjusted using FFmpeg `atempo` filters to ensure the duration of every sentence matches the original Farsi speech.
- **Simple UI**: Includes an easy-to-use Gradio web interface.

## Prerequisites

You need `python 3.9+` and system-level `ffmpeg` installed.

### Installing FFmpeg
- **Ubuntu/Debian**:
  ```bash
  sudo apt-get update && sudo apt-get install -y ffmpeg
  ```
- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```
- **Windows**:
  Download the essentials build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via winget:
  ```bash
  winget install ffmpeg
  ```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Offline TTS Voice Model**:
   This project uses a high-quality Piper TTS voice (`en_US-lessac-medium`). Run the following commands to create the `models` folder and download the `.onnx` weights and `.json` config:
   ```bash
   mkdir -p models
   wget -qO models/en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
   wget -qO models/en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
   ```
   *(Note: The Whisper model weights will be downloaded automatically the first time you run the tool).*

## Usage

Start the web interface:
```bash
python app.py
```

1. Open your browser and go to `http://localhost:7860`.
2. Upload a **Farsi `.mp3` audio file**.
3. Click **"Dub Audio to English"**.
4. The tool will process the file. Once finished, you can play and download the newly synchronized English MP3 right from the UI, and see the exact segment translations.

## Troubleshooting & GPU Acceleration

By default, PyTorch and OpenAI Whisper will attempt to use your GPU (CUDA) to process the audio quickly.

If you are using an older NVIDIA GPU (like the GeForce MX350, with a Compute Capability of `< 7.0`), the default PyTorch binaries will not be able to execute kernels on your device.

**This tool automatically detects this issue** and will print a warning in the console: `"Failed to load model on default device, falling back to CPU"`. It will then safely process the audio using your CPU. However, CPU processing will be significantly slower.

If you want to compile PyTorch from source to support your older GPU architecture (e.g., `sm_61`), please follow the advanced instructions on the [PyTorch Get Started](https://pytorch.org/get-started/locally/) page.
