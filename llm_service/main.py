"""
main.py

FastAPI application for the LLM service.
This is the "reasoning engine" that assistant_core will call.
"""

from fastapi import FastAPI

from .router import router as llm_router


app = FastAPI(
    title="Rodrix LLM Service",
    description="Reasoning engine for the Rodrix assistant.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Simple health endpoint to confirm the LLM service is running.
    """
    return {
        "status": "ok",
        "service": "llm_service",
    }


# Include all LLM-related routes (e.g. /generate)
app.include_router(llm_router)
