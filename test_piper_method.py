from piper.voice import PiperVoice
import wave

model_path = "models/en_US-lessac-medium.onnx"
voice = PiperVoice.load(model_path)
with wave.open("test_piper.wav", "wb") as wav_file:
    try:
        voice.synthesize_wav("Hello", wav_file)
        print("synthesize_wav worked")
    except Exception as e:
        print(f"synthesize_wav failed: {e}")
    try:
        voice.synthesize("Hello", wav_file)
        print("synthesize worked")
    except Exception as e:
        print(f"synthesize failed: {e}")
