import re


class LanguageDetector:

    @staticmethod
    def detect(text):
        """
        Lightweight Unicode-based language detection.

        Supported:
        English
        Tamil
        Hindi
        Telugu
        Malayalam
        Kannada
        """

        if not text:
            return "English"

        # Remove numbers, punctuation and spaces
        text = str(text)

        # Count characters belonging to each script
        tamil = len(re.findall(r'[\u0B80-\u0BFF]', text))
        hindi = len(re.findall(r'[\u0900-\u097F]', text))
        telugu = len(re.findall(r'[\u0C00-\u0C7F]', text))
        malayalam = len(re.findall(r'[\u0D00-\u0D7F]', text))
        kannada = len(re.findall(r'[\u0C80-\u0CFF]', text))

        counts = {
            "Tamil": tamil,
            "Hindi": hindi,
            "Telugu": telugu,
            "Malayalam": malayalam,
            "Kannada": kannada,
        }

        detected_language = max(
            counts,
            key=counts.get
        )

        # If no Indian-language script was detected,
        # treat the input as English.
        if counts[detected_language] == 0:
            return "English"

        return detected_language