import os
import wave
import subprocess
import urllib.request
from pydub import AudioSegment
from piper.voice import PiperVoice

def download_piper_model(model_name):
    """Automatically downloads Piper TTS models from HuggingFace if they are missing."""
    os.makedirs("models", exist_ok=True)
    base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/{model_name.split('-')[1]}/medium/{model_name}"

    onnx_path = os.path.join("models", f"{model_name}.onnx")
    json_path = os.path.join("models", f"{model_name}.onnx.json")

    if not os.path.exists(onnx_path):
        print(f"Downloading {model_name}.onnx...")
        urllib.request.urlretrieve(f"{base_url}.onnx", onnx_path)

    if not os.path.exists(json_path):
        print(f"Downloading {model_name}.onnx.json...")
        urllib.request.urlretrieve(f"{base_url}.onnx.json", json_path)

def generate_tts_piper(voice, text, output_path):
    with wave.open(output_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

def synchronize_audio(segments, output_audio_path, tts_voice_model="en_US-lessac-medium", sample_rate=22050, progress_callback=None):
    # Ensure temporary directory exists
    os.makedirs("temp_audio", exist_ok=True)

    # Auto-download models if missing
    download_piper_model(tts_voice_model)

    # Load Piper model once
    if progress_callback:
        progress_callback(0.5, f"Loading TTS model '{tts_voice_model}'...")

    model_path = os.path.join("models", f"{tts_voice_model}.onnx")
    voice = PiperVoice.load(model_path)

    # Start with silence but ensure it has the right sample rate
    final_audio = AudioSegment.silent(duration=0, frame_rate=sample_rate)

    total_segments = len(segments)
    for i, segment in enumerate(segments):
        if progress_callback:
            progress_val = 0.5 + (0.5 * (i / total_segments))
            progress_callback(progress_val, f"Synthesizing segment {i+1} of {total_segments}...")

        start = segment["start"] * 1000 # convert to ms
        end = segment["end"] * 1000 # convert to ms
        duration = end - start

        if duration <= 0:
            continue

        text = segment["text"]
        if not text:
            continue

        temp_wav = f"temp_audio/segment_{i}.wav"
        temp_adjusted_wav = f"temp_audio/adjusted_{i}.wav"

        # 1. Generate English TTS
        print(f"Synthesizing: '{text}'")
        generate_tts_piper(voice, text, temp_wav)

        # 2. Check duration of TTS
        tts_audio = AudioSegment.from_wav(temp_wav)
        tts_duration = len(tts_audio)

        # if TTS is extremely short or generation failed, skip adjustment
        if tts_duration == 0:
            print(f"  Skipping segment {i} because TTS duration is 0ms")
            continue

        # 3. Synchronize using ffmpeg (atempo filter)
        ratio = tts_duration / duration
        print(f"  Segment {i}: target duration={duration}ms, TTS duration={tts_duration}ms, ratio={ratio:.2f}")

        # ffmpeg atempo supports [0.5, 100.0] ratios.
        # If it's too fast or too slow we might need multiple atempos, but typical speech fits in this bound.
        # To change duration, we need an atempo factor of `ratio`.
        # E.g., if TTS is 2000ms and we want 1000ms, ratio is 2.0 -> we speed up by 2x.

        # Keep ratio in safe bounds just in case (e.g., 0.5 to 2.0 per single filter, but ffmpeg does up to 100.0)
        # It's safer to constrain ratio to avoid extreme distortion. Let's cap atempo to between 0.5 and 2.5
        atempo = ratio
        if atempo < 0.5:
            atempo = 0.5
        elif atempo > 3.0:
            atempo = 3.0

        subprocess.run([
            "ffmpeg", "-y", "-i", temp_wav,
            "-filter:a", f"atempo={atempo}",
            temp_adjusted_wav
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Load the synchronized segment
        synced_segment = AudioSegment.from_wav(temp_adjusted_wav)

        # 4. Insert into timeline
        current_len = len(final_audio)
        if current_len < start:
            # Need to pad with silence until the start time
            padding_duration = start - current_len
            final_audio += AudioSegment.silent(duration=padding_duration)
        elif current_len > start:
            # Overlap handling (if previous segment bled over)
            # Simplest approach: just append it. It will push timestamps out slightly,
            # but usually fine if we clamped atempo correctly.
            pass

        final_audio += synced_segment

        # Cleanup temp files
        os.remove(temp_wav)
        os.remove(temp_adjusted_wav)

    # Export final audio as mp3
    print(f"Exporting final audio to {output_audio_path}")
    final_audio.export(output_audio_path, format="mp3")

    # Clean up temp dir
    try:
        os.rmdir("temp_audio")
    except OSError:
        pass

    return output_audio_path

if __name__ == "__main__":
    sample_segments = [
        {"start": 0.0, "end": 2.5, "text": "Hello, this is a test segment."},
        {"start": 3.0, "end": 6.0, "text": "And here is another one that follows."}
    ]
    synchronize_audio(sample_segments, "test_output.mp3")
    print("Done testing TTS synchronization.")
