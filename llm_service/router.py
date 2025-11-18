"""
router.py

Defines the HTTP API routes for the LLM service.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from .model_client import llm_client


router = APIRouter()


class GenerateRequest(BaseModel):
    """
    Request body for /generate.
    """
    prompt: str


class GenerateResponse(BaseModel):
    """
    Response body for /generate.
    """
    output: str


@router.post("/generate", response_model=GenerateResponse)
def generate_text(req: GenerateRequest):
    """
    Generate text from a prompt using the underlying LLM client.

    For now, this calls MockLLMClient, which returns a scripted response.
    Later, this will call a real model.
    """
    output_text = llm_client.generate(req.prompt)
    return GenerateResponse(output=output_text)
