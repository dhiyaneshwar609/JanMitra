import ollama


class LocalLLM:
    def __init__(self, model="qwen2.5:1.5b"):
        self.model = model

    def stream(self, prompt: str):
        """
        Stream response from Ollama.
        """
        stream = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
            options={
                "temperature": 0.1,
                "num_predict": 768,
                "num_ctx": 4096,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        )

        for chunk in stream:
            text = chunk["message"]["content"]
            yield text

    def generate(self, prompt: str):
        """
        Return the complete response (used by existing code).
        """
        return "".join(self.stream(prompt))