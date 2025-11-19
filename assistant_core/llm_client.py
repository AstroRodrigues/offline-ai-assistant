"""
llm_client.py

Client used by assistant_core to call the LLM service.
For now it calls the mock /generate endpoint on port 8001.
"""

import httpx


class LLMClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        """
        Call the LLM service /generate endpoint with the given prompt.
        Returns the 'output' text from the LLM.
        """
        url = f"{self.base_url}/generate"
        payload = {"prompt": prompt}

        # simple synchronous request – enough for now
        try:
            resp = httpx.post(url, json=payload, timeout=60.0)
            resp.raise_for_status()
        except httpx.RequestError:
            # LLM service unreachable / network error
            return (
                "Rodrix: LLM service is unreachable. "
                "My reasoning core appears to be offline."
            )
        except httpx.HTTPStatusError as e:
            # LLM service responded but with error status
            return (
                f"Rodrix: LLM service returned an error status: {e.response.status_code}. "
                "Reasoning is temporarily unavailable."
            )

        data = resp.json()
        # expecting { "output": "..." }
        return data.get("output", "Rodrix: LLM service responded with an unexpected format.")


# default instance that main.py can use
llm_client = LLMClient()
