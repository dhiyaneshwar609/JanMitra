import fitz
import requests
import tempfile
import os
import traceback


class PDFExtractor:

    def __init__(self, timeout=30):

        self.timeout = timeout

        self.headers = {
            "User-Agent": "CitizenAI/1.0"
        }

    def extract(self, url):

        temp_path = None

        try:

            print("Downloading:", url)

            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                stream=True
            )

            print("Status Code:", response.status_code)

            if response.status_code != 200:
                print("Failed to download PDF")
                return None

            print("Saving PDF...")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

                temp_path = f.name

            doc = fitz.open(temp_path)

            text = []

            for page in doc:
                text.append(page.get_text())

            doc.close()

            return {
                "url": url,
                "title": os.path.basename(url),
                "content": "\n".join(text),
                "content_type": "pdf"
            }

        except Exception as e:
            print("PDF Extraction Error:")
            traceback.print_exc()
            return None

        finally:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            