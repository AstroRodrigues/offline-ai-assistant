"""
model_client.py

This module is responsible for talking to the language model.

- OllamaLLMClient: talks to a local Ollama server via HTTP.
- MockLLMClient: fallback / testing client.

llm_client: the default client used by the service.
"""

import httpx


class OllamaLLMClient:
    """
    LLM client that uses a local Ollama server.

    It sends POST requests to http://localhost:11434/api/generate
    with the chosen model name and prompt.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str) -> str:
        prompt = prompt.strip()
        if not prompt:
            return "Rodrix: No input received."

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # simpler: get the full response at once
        }

        try:
            resp = httpx.post(url, json=payload, timeout=60.0)
            resp.raise_for_status()
        except httpx.RequestError:
            return (
                "Rodrix: I attempted to contact my local reasoning engine (Ollama), "
                "but the service is unreachable."
            )
        except httpx.HTTPStatusError as e:
            return (
                f"Rodrix: The local LLM backend returned an error status: "
                f"{e.response.status_code}. Reasoning is temporarily unavailable."
            )

        data = resp.json()
        # Ollama returns { "model": "...", "created_at": "...", "response": "..." , ...}
        text = data.get("response", "").strip()
        if not text:
            return "Rodrix: The LLM responded with an empty output."

        return text


class MockLLMClient:
    """
    Simple mock client used for testing or as a fallback.
    """

    def generate(self, prompt: str) -> str:
        prompt = prompt.strip()
        if not prompt:
            return "Rodrix: No input received."

        return (
            "Rodrix: I have received your prompt. "
            f"You said: '{prompt}'. "
            "At this stage I am using a mock reasoning core, "
            "so this is a scripted response rather than true inference."
        )


# Choose which client to use here:
# llm_client = MockLLMClient()
llm_client = OllamaLLMClient()
