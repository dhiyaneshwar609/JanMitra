import os
import wave
import numpy as np
import onnxruntime as ort


MODEL_PATH = r"app\voice\models\indic\ta\model.int8.onnx"
AUDIO_PATH = r"app\voice\tamil_test.wav"


print("Loading Tamil IndicConformer model...")

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

print("Tamil model loaded successfully.")

print("\nOpening audio:", AUDIO_PATH)

with wave.open(AUDIO_PATH, "rb") as wf:

    sample_rate = wf.getframerate()
    channels = wf.getnchannels()
    sample_width = wf.getsampwidth()
    frames = wf.readframes(wf.getnframes())

print("Sample rate:", sample_rate)
print("Channels:", channels)
print("Sample width:", sample_width)

audio = np.frombuffer(
    frames,
    dtype=np.int16
).astype(np.float32)

audio = audio / 32768.0

if channels != 1:
    raise ValueError("Audio must be mono.")

audio = np.expand_dims(audio, axis=0)

length = np.array(
    [audio.shape[1]],
    dtype=np.int64
)

outputs = session.run(
    None,
    {
        "audio_signal": audio,
        "length": length
    }
)

print("\nTamil model inference completed successfully.")

print("Output shape:", outputs[0].shape)
print("\nThe model successfully processed the audio.")