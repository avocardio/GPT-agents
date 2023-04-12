import numpy as np
import sounddevice as sd
import openai
import json
import os
import threading
from scipy.io.wavfile import write

with open("credentials.json", "r") as file:
    credentials = json.load(file)

OPENAI_API_KEY = credentials.get("OPENAI_API_KEY")

def transcribe():

    # Record audio
    def record_audio(stop_event):
        sample_rate = 16000
        audio_data = []

        def audio_callback(indata, frames, time, status):
            if stop_event.is_set():
                raise sd.CallbackStop
            audio_data.append(np.array(indata))

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, callback=audio_callback):
                # print("(Recording... Press Enter to stop).")
                stop_event.wait()
        except KeyboardInterrupt:
            exit()

        audio_data = np.concatenate(audio_data, axis=0)
        return audio_data

    # Save audio as WAV
    def save_audio_as_wav(audio, filename):
        audio = (audio * 32768).astype(np.int16)
        write(filename, 16000, audio)

    # Record audio until Enter is pressed
    stop_event = threading.Event()
    threading.Thread(target=lambda: input() or stop_event.set()).start()
    audio_data = record_audio(stop_event)

    # Save recorded audio as a WAV file
    wav_filename = "utils/openai.wav"
    save_audio_as_wav(audio_data, wav_filename)

    # Set the OpenAI API key
    openai.api_key = OPENAI_API_KEY

    # Transcribe the audio
    with open("utils/openai.wav", "rb") as file:
        response = openai.Audio.transcribe(model="whisper-1", file=file)

    # Remove the WAV file
    os.remove("utils/openai.wav")

    return response['text']