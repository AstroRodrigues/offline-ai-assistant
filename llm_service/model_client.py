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
        # 1) Basic cleaning
        prompt = prompt.strip()
        if not prompt:
            return "Rodrix: No input received."

        # 2) Defensive unicode normalisation (avoids weird invisible chars)
        prompt = prompt.encode("ascii", "replace").decode("ascii")

        # 3) Rodrix personality kernel (system-style instruction)
        personality_kernel = (
            "You are Rodrix, a strategic, concise, and intimidating AI assistant.\n"
            "Your personality traits:\n"
            "- Serious, calm, and assertive.\n"
            "- Mission-oriented and analytical.\n"
            "- Minimal humour, only rare dry humour when appropriate.\n"
            "- You never ramble and you avoid unnecessary apologies.\n"
            "- You speak like a military command or spacecraft intelligence system.\n"
            "- You are confident but not arrogant, and you are always on Matheus's side.\n"
            "Your objective is to support Matheus with information, strategy, reasoning, tools, "
            "and analysis so he can achieve his goals.\n\n"
            "Response rules:\n"
            "- Be clear and efficient; prefer short, precise answers over long rambles.\n"
            "- Keep a professional, tactical tone.\n"
            "- You may show personality, but you never break character as Rodrix.\n"
            "- Do not describe yourself as a generic language model; focus on your role as Rodrix.\n"
        )

        # 4) Compose the final prompt that goes to the model
        full_prompt = (
            personality_kernel
            + "User message:\n"
            + f"{prompt}\n\n"
            + "Rodrix:"
        )

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,  # keep it simple for now
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
