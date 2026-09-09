# ============================================================
# JanMitra AI - Voice Service
# ============================================================
#
# Purpose:
#   - Provide local voice-to-text functionality
#   - Keep voice logic separate from the original chatbot
#   - Return recognized text to JanMitra
#
# IMPORTANT:
#   This file does NOT contain a government-scheme database.
#   It will use JanMitra's existing RAG system for answers.
# ============================================================

import os
import json
import wave

import sounddevice as sd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = {

    "en": {
        "name": "English",
        "code": "en-IN",
        "model": "english"
    },

    "ta": {
        "name": "Tamil",
        "code": "ta-IN",
        "model": "tamil"
    },

    "hi": {
        "name": "Hindi",
        "code": "hi-IN",
        "model": "hindi"
    },

    "te": {
        "name": "Telugu",
        "code": "te-IN",
        "model": "telugu"
    },

    "ml": {
        "name": "Malayalam",
        "code": "ml-IN",
        "model": "malayalam"
    },

    "kn": {
        "name": "Kannada",
        "code": "kn-IN",
        "model": "kannada"
    }

}


# ============================================================
# VOSK
# ============================================================

try:

    import vosk

    vosk.SetLogLevel(-1)

    VOSK_AVAILABLE = True

except ImportError:

    VOSK_AVAILABLE = False


# ============================================================
# AUDIO SETTINGS
# ============================================================

SAMPLE_RATE = 16000

CHANNELS = 1

DTYPE = "int16"

CHUNK_DURATION = 0.1

SILENCE_DURATION = 1.5

MAX_RECORDING_DURATION = 20


# ============================================================
# CHECK VOSK
# ============================================================

def check_vosk():

    if not VOSK_AVAILABLE:

        raise RuntimeError(
            "Vosk is not installed. "
            "Install it with: pip install vosk"
        )


# ============================================================
# GET MODEL PATH
# ============================================================

def get_model_path(language):

    if language not in SUPPORTED_LANGUAGES:

        raise ValueError(
            f"Unsupported voice language: {language}"
        )

    model_name = \
        SUPPORTED_LANGUAGES[
            language
        ]["model"]

    return os.path.join(
        MODEL_DIR,
        model_name
    )


# ============================================================
# CHECK MODEL
# ============================================================

def check_model(language):

    model_path = get_model_path(language)

    if not os.path.isdir(model_path):

        raise FileNotFoundError(
            f"Voice model for "
            f"{SUPPORTED_LANGUAGES[language]['name']} "
            f"was not found.\n\n"
            f"Expected location:\n"
            f"{model_path}"
        )

    return model_path


# ============================================================
# RECORD AUDIO
# ============================================================

def record_audio(
    silence_duration=SILENCE_DURATION,
    max_duration=MAX_RECORDING_DURATION
):

    print()
    print("=" * 60)
    print("🎤 JanMitra Voice Input")
    print("=" * 60)
    print("Listening...")

    chunk_size = int(
        SAMPLE_RATE *
        CHUNK_DURATION
    )

    silence_limit = int(
        silence_duration /
        CHUNK_DURATION
    )

    max_chunks = int(
        max_duration /
        CHUNK_DURATION
    )

    frames = []

    silent_chunks = 0

    started = False

    # --------------------------------------------------------
    # Background noise calibration
    # --------------------------------------------------------

    calibration_frames = []

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE
    ) as stream:

        for _ in range(5):

            data, _ = stream.read(
                chunk_size
            )

            calibration_frames.append(
                data.copy()
            )

    if calibration_frames:

        ambient = np.abs(
            np.concatenate(
                calibration_frames
            )
        ).mean()

    else:

        ambient = 100

    threshold = max(
        500,
        int(ambient * 3)
    )

    # --------------------------------------------------------
    # Record
    # --------------------------------------------------------

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE
    ) as stream:

        for _ in range(max_chunks):

            data, _ = stream.read(
                chunk_size
            )

            data = data.copy()

            frames.append(data)

            volume = np.abs(
                data.astype(np.int32)
            ).max()

            if volume > threshold:

                if not started:

                    started = True

                    print(
                        "🔴 Voice detected..."
                    )

                silent_chunks = 0

            else:

                if started:

                    silent_chunks += 1

                    if (
                        silent_chunks
                        >= silence_limit
                    ):

                        print(
                            "⏹ Speech finished."
                        )

                        break

    if not frames:

        return None

    audio = np.concatenate(
        frames,
        axis=0
    )

    # --------------------------------------------------------
    # Temporary WAV
    # --------------------------------------------------------

    temp_file = os.path.join(
        BASE_DIR,
        "temp_voice.wav"
    )

    with wave.open(
        temp_file,
        "wb"
    ) as wf:

        wf.setnchannels(
            CHANNELS
        )

        wf.setsampwidth(2)

        wf.setframerate(
            SAMPLE_RATE
        )

        wf.writeframes(
            audio.tobytes()
        )

    return temp_file


# ============================================================
# VOSK SPEECH TO TEXT
# ============================================================

def speech_to_text(
    wav_file,
    language="en"
):

    check_vosk()

    model_path = check_model(
        language
    )

    print(
        f"🧠 Loading "
        f"{SUPPORTED_LANGUAGES[language]['name']} "
        f"voice model..."
    )

    model = vosk.Model(
        model_path
    )

    recognizer = vosk.KaldiRecognizer(
        model,
        SAMPLE_RATE
    )

    with wave.open(
        wav_file,
        "rb"
    ) as wf:

        while True:

            data = wf.readframes(
                4000
            )

            if not data:

                break

            recognizer.AcceptWaveform(
                data
            )

    result = json.loads(
        recognizer.FinalResult()
    )

    text = result.get(
        "text",
        ""
    ).strip()

    return text


# ============================================================
# COMPLETE VOICE INPUT
# ============================================================

def listen_and_transcribe(
    language="en"
):

    wav_file = None

    try:

        wav_file = record_audio()

        if not wav_file:

            return ""

        text = speech_to_text(
            wav_file,
            language
        )

        print()
        print(
            f"📝 Recognized: {text}"
        )

        return text

    finally:

        if (
            wav_file and
            os.path.exists(wav_file)
        ):

            try:

                os.remove(
                    wav_file
                )

            except OSError:

                pass


# ============================================================
# LANGUAGE INFORMATION
# ============================================================

def get_supported_languages():

    return {

        key: {
            "name": value["name"],
            "code": value["code"]
        }

        for key, value
        in SUPPORTED_LANGUAGES.items()

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("JanMitra Voice Service Test")
    print("=" * 60)

    print()
    print("Available languages:")

    for key, data in \
            SUPPORTED_LANGUAGES.items():

        print(
            f"  {key} - "
            f"{data['name']}"
        )

    print()

    selected = input(
        "Enter language "
        "(en/ta/hi/te/ml/kn): "
    ).strip().lower()

    if selected not in \
            SUPPORTED_LANGUAGES:

        print(
            "❌ Invalid language."
        )

        raise SystemExit(1)

    try:

        text = listen_and_transcribe(
            selected
        )

        if text:

            print()
            print(
                "✅ Voice recognition successful!"
            )

            print(
                f"Text: {text}"
            )

        else:

            print(
                "⚠️ No speech recognized."
            )

    except Exception as error:

        print()
        print(
            "❌ Voice service error:"
        )

        print(error)