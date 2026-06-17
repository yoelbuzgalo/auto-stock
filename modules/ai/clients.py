import json
import time
import requests


class OllamaClient:
    """
    Maintains a reusable HTTP session for Ollama inference requests.
    """

    def __init__(self, url, model, timeout=60):
        """
        Initializes a persistent Ollama client.

        Args:
            url (str): Ollama generation endpoint URL.
            model (str): Ollama model name.
            timeout (int): Request timeout in seconds.
        """
        self.url = url
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()

    def stream_prompt(self, prompt):
        """
        Streams response tokens from Ollama.

        Args:
            prompt (str): Full prompt text sent to the model.

        Yields:
            str: Response token text.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": "30m"
        }

        with self.session.post(
            self.url,
            json=payload,
            timeout=self.timeout,
            stream=True
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line.decode("utf-8"))
                token = chunk.get("response", "")

                if token:
                    yield token

    def close(self):
        """
        Closes the persistent HTTP session.
        """
        self.session.close()