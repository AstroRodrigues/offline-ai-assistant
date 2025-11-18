"""
model_client.py

This module is responsible for talking to the language model.
For now, it's a simple mock implementation so we can test
end-to-end flow without a real LLM.
"""


class MockLLMClient:
    """
    Very simple mock LLM.

    Later, you can replace this with:
    - a call to Ollama
    - a local GPU model
    - or any other LLM backend.
    """

    def generate(self, prompt: str) -> str:
        prompt = prompt.strip()
        if not prompt:
            return "Rodrix: No input received."

        # Very simple placeholder behaviour with Rodrix flavour.
        return (
            "Rodrix: I have received your prompt. "
            f"You said: '{prompt}'. "
            "At this stage I am using a mock reasoning core, "
            "so this is a scripted response rather than true inference."
        )


# Default client instance used by the router
llm_client = MockLLMClient()
