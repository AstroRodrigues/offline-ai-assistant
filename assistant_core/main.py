#from fastapi import FastAPI
#
#app = FastAPI()
#
#@app.get("/health")
#def health():
#    return {"status": "ok", "message": "minimal core is running"}

from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import yaml

# ---------- Load settings from configs/settings.yaml ----------

class AssistantSettings(BaseModel):
    name: str
    persona: str
    language: str
    wake_word: str
    humor_level: str

class Settings(BaseModel):
    assistant: AssistantSettings

def load_settings() -> Settings:
    """
    Load the assistant settings from configs/settings.yaml so
    the core knows things like the name (Rodrix), persona, etc.
    """
    root = Path(__file__).resolve().parents[1]
    config_path = root / "configs" / "settings.yaml"

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return Settings(**raw)

settings = load_settings()

# ---------- FastAPI app ----------

app = FastAPI(
    title="Rodrix Assistant Core",
    description="Core brain of the Rodrix strategic intelligence assistant.",
    version="0.1.0",
)

# ---------- Request / response models ----------

class ChatRequest(BaseModel):
    user_id: str = "matheus"
    message: str

class ChatResponse(BaseModel):
    assistant_name: str
    reply: str

# ---------- Routes ----------

@app.get("/health")
def health_check():
    """
    Simple health endpoint to confirm the service is running
    and using the right assistant settings.
    """
    return {
        "status": "ok",
        "assistant": settings.assistant.name,
        "persona": settings.assistant.persona,
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    First placeholder version of /chat.

    For now:
    - It reads the message.
    - It responds with a simple acknowledgement in a Rodrix-style tone.

    Later:
    - This will call the LLM service.
    - It will call tools based on tools.yaml.
    - It will build proper responses and actions.
    """
    text = req.message.strip()

    if not text:
        rodrix_reply = "No input detected."
    else:
        rodrix_reply = (
            f"{req.user_id}, I received your message: '{text}'. "
            "My higher reasoning core is not online yet, "
            "but the communication channel is operational."
        )

    return ChatResponse(
        assistant_name=settings.assistant.name,
        reply=rodrix_reply,
    )
