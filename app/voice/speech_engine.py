import os
import json
import wave

import numpy as np
import onnxruntime as ort
from vosk import Model, KaldiRecognizer


class SpeechEngine:

    def __init__(self):

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        # ==========================================
        # English Vosk
        # ==========================================

        self.english_model_path = os.path.join(
            self.base_dir,
            "models",
            "english"
        )

        self.english_model = None

        # ==========================================
        # IndicConformer models
        # ==========================================

        self.indic_base_path = os.path.join(
            self.base_dir,
            "models",
            "indic"
        )

        self.indic_models = {}

        self.languages = {
            "hi": "Hindi",
            "kn": "Kannada",
            "ml": "Malayalam",
            "ta": "Tamil",
            "te": "Telugu"
        }

    # ==========================================
    # Load English Vosk
    # ==========================================

    def load_english(self):

        if self.english_model is None:

            if not os.path.isdir(
                self.english_model_path
            ):
                raise FileNotFoundError(
                    "English Vosk model not found: "
                    + self.english_model_path
                )

            print("Loading English Vosk model...")

            self.english_model = Model(
                self.english_model_path
            )

            print("English Vosk model loaded.")

        return self.english_model

    # ==========================================
    # Load IndicConformer model
    # ==========================================

    def load_indic(self, language_code):

        if language_code not in self.languages:

            raise ValueError(
                f"Unsupported language: {language_code}"
            )

        if language_code in self.indic_models:

            return self.indic_models[
                language_code
            ]

        model_path = os.path.join(
            self.indic_base_path,
            language_code,
            "model.int8.onnx"
        )

        if not os.path.isfile(model_path):

            raise FileNotFoundError(
                "IndicConformer model not found: "
                + model_path
            )

        print(
            f"Loading {self.languages[language_code]} "
            f"speech model..."
        )

        session = ort.InferenceSession(
            model_path,
            providers=[
                "CPUExecutionProvider"
            ]
        )

        self.indic_models[
            language_code
        ] = session

        print(
            f"{self.languages[language_code]} "
            "speech model loaded."
        )

        return session

    # ==========================================
    # English speech recognition
    # ==========================================

    def transcribe_english(
        self,
        audio_path
    ):

        model = self.load_english()

        with wave.open(
            audio_path,
            "rb"
        ) as wf:

            if wf.getnchannels() != 1:

                raise ValueError(
                    "Audio must be mono."
                )

            sample_rate = wf.getframerate()

            recognizer = KaldiRecognizer(
                model,
                sample_rate
            )

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

    # ==========================================
    # IndicConformer recognition
    # ==========================================

    def transcribe_indic(
        self,
        audio_path,
        language_code
    ):

        session = self.load_indic(
            language_code
        )

        with wave.open(
            audio_path,
            "rb"
        ) as wf:

            sample_rate = wf.getframerate()

            channels = wf.getnchannels()

            if channels != 1:

                raise ValueError(
                    "Audio must be mono."
                )

            frames = wf.readframes(
                wf.getnframes()
            )

        audio = np.frombuffer(
            frames,
            dtype=np.int16
        ).astype(np.float32)

        audio = audio / 32768.0

        audio = np.expand_dims(
            audio,
            axis=0
        )

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

        return outputs

    # ==========================================
    # Main entry point
    # ==========================================

    def transcribe(
        self,
        audio_path,
        language_code="en"
    ):

        if language_code == "en":

            text = self.transcribe_english(
                audio_path
            )

            return {
                "text": text,
                "language": "en-IN"
            }

        if language_code in self.languages:

            outputs = self.transcribe_indic(
                audio_path,
                language_code
            )

            return {
                "text": "",
                "language": language_code,
                "raw_output": outputs
            }

        raise ValueError(
            f"Unsupported language: {language_code}"
        )