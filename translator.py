import whisper

def transcribe_and_translate(audio_path):
    print(f"Loading Whisper model...")
    # Load the base model to be fast enough while providing decent accuracy
    model = whisper.load_model("base")
    print(f"Translating audio: {audio_path}")

    # transcribe with task="translate" to translate Farsi to English
    result = model.transcribe(audio_path, task="translate")

    segments = []
    for segment in result["segments"]:
        segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })
        print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")

    return segments

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        transcribe_and_translate(sys.argv[1])
