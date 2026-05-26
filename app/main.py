"""
main.py

FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import PrioritizeRequest, PrioritizeResponse
from .prioritizer import RequirementPrioritizer

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prioritizer: Optional[RequirementPrioritizer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global prioritizer
    model_name = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
    logger.info("Initialising prioritizer with model: %s", model_name)
    prioritizer = RequirementPrioritizer(model_name=model_name)
    yield
    prioritizer = None


app = FastAPI(
    title="AI Requirements Prioritizer",
    description="LLM-powered API for automatic software requirement prioritization",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": prioritizer is not None}


@app.post("/prioritize", response_model=PrioritizeResponse)
async def prioritize_requirements(request: PrioritizeRequest):
    if prioritizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    results = prioritizer.prioritize(request.requirements, request.weights)

    if not results:
        raise HTTPException(status_code=500, detail="Failed to score any requirements")

    return PrioritizeResponse(
        results=results,
        model_used=prioritizer.model_name,
        total_requirements=len(results),
    )
