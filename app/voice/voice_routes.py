from flask import Blueprint, request, jsonify
import os
import tempfile
import wave
import json

from vosk import Model, KaldiRecognizer


voice_api = Blueprint("voice_api", __name__)


# ============================================================
# VOSK MODEL
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "english"
)

_model = None


def get_model():

    global _model

    if _model is None:

        if not os.path.isdir(MODEL_PATH):

            raise FileNotFoundError(
                f"Vosk model not found: {MODEL_PATH}"
            )

        _model = Model(MODEL_PATH)

    return _model


# ============================================================
# VOICE → TEXT
# ============================================================

@voice_api.route(
    "/voice-to-text",
    methods=["POST"]
)
def voice_to_text():

    temp_file = None

    try:

        if "audio" not in request.files:

            return jsonify({
                "error": "No audio file received."
            }), 400

        audio_file = request.files["audio"]

        if not audio_file.filename:

            return jsonify({
                "error": "Empty audio file."
            }), 400


        # Save temporary WAV
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp:

            temp_file = temp.name

        audio_file.save(temp_file)


        # Load Vosk
        model = get_model()


        # Read WAV
        with wave.open(
            temp_file,
            "rb"
        ) as wf:

            if wf.getnchannels() != 1:

                return jsonify({
                    "error":
                    "Audio must be mono."
                }), 400

            sample_rate = wf.getframerate()

            recognizer = KaldiRecognizer(
                model,
                sample_rate
            )


            while True:

                data = wf.readframes(4000)

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


        return jsonify({

            "success": True,

            "text": text,

            "language": "en-IN"

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


    finally:

        if (
            temp_file and
            os.path.exists(temp_file)
        ):

            try:
                os.remove(temp_file)
            except OSError:
                pass