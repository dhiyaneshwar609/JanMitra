import json
import os
import wave

import sounddevice as sd
from vosk import Model, KaldiRecognizer


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "english"
)

SAMPLE_RATE = 16000
CHANNELS = 1


print("Loading Vosk English model...")
model = Model(MODEL_PATH)

recognizer = KaldiRecognizer(
    model,
    SAMPLE_RATE
)

print()
print("🎤 Speak now...")
print("Recording for 8 seconds...")
print()

audio = sd.rec(
    int(8 * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

print("⏹ Recording finished.")
print("🧠 Processing speech...")

recognizer.AcceptWaveform(
    audio.tobytes()
)

result = json.loads(
    recognizer.FinalResult()
)

text = result.get(
    "text",
    ""
).strip()

print()
print("=" * 50)
print("Recognized text:")
print(text if text else "[No speech recognized]")
print("=" * 50)