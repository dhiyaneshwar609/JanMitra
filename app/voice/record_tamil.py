import sounddevice as sd
import wave

OUTPUT_FILE = r"app\voice\tamil_test.wav"

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 8

print("🎤 Speak Tamil now...")
print(f"Recording for {DURATION} seconds...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

with wave.open(OUTPUT_FILE, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio.tobytes())

print("\n✅ Tamil recording saved:")
print(OUTPUT_FILE)