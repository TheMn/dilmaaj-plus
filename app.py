import gradio as gr
import os
from translator import transcribe_and_translate
from synchronizer import synchronize_audio

def process_audio(farsi_audio_path, whisper_model, tts_voice, progress=gr.Progress()):
    if not farsi_audio_path:
        return None, "No audio provided."

    def progress_callback(fraction, desc):
        progress(fraction, desc=desc)

    try:
        # Step 1: Transcribe and translate
        print(f"Processing uploaded file: {farsi_audio_path}")
        segments = transcribe_and_translate(
            farsi_audio_path,
            whisper_model=whisper_model,
            progress_callback=progress_callback
        )

        # Format the text segments for display
        transcription_text = ""
        for seg in segments:
            transcription_text += f"[{seg['start']:.2f} - {seg['end']:.2f}]: {seg['text']}\n"

        import uuid
        import tempfile
        # Step 2: Synchronize and generate English audio
        # Use a temporary directory to save the output file so it gets cleaned up by the OS
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, f"english_dubbed_{uuid.uuid4().hex[:8]}.mp3")

        final_audio_path = synchronize_audio(
            segments,
            output_file,
            tts_voice_model=tts_voice,
            progress_callback=progress_callback
        )

        progress(1.0, desc="Done!")
        return final_audio_path, transcription_text
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"An error occurred: {str(e)}"

# Define the Gradio interface
with gr.Blocks(title="Farsi to English AI Dubbing Tool") as demo:
    gr.Markdown("# Farsi to English AI Dubbing Tool")
    gr.Markdown("Upload a Farsi audio file (e.g., `.mp3`). This tool will transcribe the Farsi speech, translate it to English, generate a natural offline English voice using Piper TTS, and synchronize the English audio to perfectly match the original timestamps and gaps.")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(label="Upload Farsi Audio", type="filepath", sources=["upload"])

            with gr.Row():
                whisper_model_dropdown = gr.Dropdown(
                    choices=["base", "small", "medium"],
                    value="small",
                    label="Whisper Translation Quality (small/medium recommended for Farsi)"
                )
                tts_voice_dropdown = gr.Dropdown(
                    choices=["en_US-lessac-medium", "en_US-ryan-medium"],
                    value="en_US-ryan-medium",
                    label="English Voice Model (lessac=Female, ryan=Male)"
                )

            process_btn = gr.Button("Dub Audio to English", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(label="Dubbed English Audio")
            transcription_output = gr.Textbox(label="Translation Segments", lines=10)

    process_btn.click(
        fn=process_audio,
        inputs=[audio_input, whisper_model_dropdown, tts_voice_dropdown],
        outputs=[audio_output, transcription_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
