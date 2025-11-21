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
from .llm_client import llm_client
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

#@app.post("/chat", response_model=ChatResponse)
#def chat(req: ChatRequest):
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
  #  text = req.message.strip()

  #  if not text:
  #      rodrix_reply = "No input detected."
 #   else:
 #       rodrix_reply = (
  #          f"{req.user_id}, I received your message: '{text}'. "
 #           "My higher reasoning core is not online yet, "
 #           "but the communication channel is operational."
 #       )
#
 #   return ChatResponse(
 #       assistant_name=settings.assistant.name,
 #       reply=rodrix_reply,
 #   )
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    /chat endpoint.

    Flow now:
    - Take the user's message.
    - Build a prompt (we can make this richer later, with persona, context, tools).
    - Send it to the LLM service (/generate).
    - Return the LLM's answer as Rodrix's reply.
    """
    text = req.message.strip()

    if not text:
        rodrix_reply = "No input detected."
    else:
        # For now we send the raw user text as the prompt.
        # Later, we will wrap it with instructions, memory, and tool context.
        prompt = text

        # Call the LLM service
        rodrix_reply = llm_client.generate(prompt)

    return ChatResponse(
        assistant_name=settings.assistant.name,
        reply=rodrix_reply,
    )

@app.get("/tool/ping")
def tool_ping():
    """
    system.ping tool endpoint.

    This is a simple “alive check” tool used to validate the tools pipeline (checks the tools.yaml).
    It will always return quickly and never fail unless assistant_core is down.
    """
    return {
        "tool": "system.ping",
        "status": "ok",
        "message": "Tool pipeline online. Rodrix systems nominal."
    }
