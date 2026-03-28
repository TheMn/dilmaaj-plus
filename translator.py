import whisper

def transcribe_and_translate(audio_path, whisper_model="base", progress_callback=None):
    if progress_callback:
        progress_callback(0, f"Loading Whisper '{whisper_model}' model (this might take a while on first run)...")
    else:
        print(f"Loading Whisper model...")

    try:
        model = whisper.load_model(whisper_model)
    except RuntimeError as e:
        print(f"Failed to load model on default device, falling back to CPU. Error: {e}")
        model = whisper.load_model(whisper_model, device="cpu")

    if progress_callback:
        progress_callback(0.2, f"Transcribing and translating audio: {audio_path}")
    else:
        print(f"Translating audio: {audio_path}")

    # transcribe with task="translate" to translate Farsi to English
    # Explicitly set language to 'fa' (Farsi/Persian) to prevent Whisper from confusing the source language
    result = model.transcribe(audio_path, task="translate", language="fa")

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
