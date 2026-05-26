"""
prioritizer.py

Core prioritization logic: calls the LLM for each requirement,
parses scores, computes weighted final score, returns ranked list.
"""

import json
import logging
import os
from typing import List, Optional

from transformers import pipeline

from .models import (
    DimensionScores, PrioritizedRequirement, Requirement,
)
from .prompts import SCORING_PROMPT, DEFAULT_WEIGHTS

logger = logging.getLogger(__name__)

# Using a smaller instruction-tuned model that can follow JSON output instructions.
# Swap for a larger model or OpenAI-compatible endpoint for better accuracy.
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"


class RequirementPrioritizer:
    def __init__(self, model_name: str = DEFAULT_MODEL, hf_token: str = None):
        token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
        logger.info("Loading model: %s", model_name)
        self.pipe = pipeline(
            "text-generation",
            model=model_name,
            token=token,
            device_map="auto",
            max_new_tokens=512,
            do_sample=False,
        )
        self.model_name = model_name

    def _score_requirement(self, req: Requirement) -> dict:
        prompt = SCORING_PROMPT.format(
            title=req.title,
            description=req.description,
            stakeholder_notes=req.stakeholder_notes or "None provided",
            dependencies=", ".join(req.dependencies) if req.dependencies else "None",
        )
        output = self.pipe(prompt)[0]["generated_text"]

        # Extract JSON portion from model output
        start = output.rfind("{")
        end = output.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"Model did not return valid JSON for requirement {req.id}")

        return json.loads(output[start:end])

    def _compute_final_score(self, scores: dict, weights: dict) -> float:
        total_weight = sum(weights.values())
        score = sum(scores[dim] * weights[dim] for dim in weights if dim in scores)
        return round(score / total_weight, 3)

    def prioritize(self, requirements: List[Requirement],
                   custom_weights: Optional[dict] = None) -> List[PrioritizedRequirement]:
        weights = {**DEFAULT_WEIGHTS, **(custom_weights or {})}
        results = []

        for req in requirements:
            try:
                raw = self._score_requirement(req)
            except Exception as e:
                logger.error("Failed to score requirement %s: %s", req.id, e)
                continue

            dim_scores = DimensionScores(
                business_value=raw["business_value"],
                stakeholder_priority=raw["stakeholder_priority"],
                implementation_effort=raw["implementation_effort"],
                risk=raw["risk"],
                dependencies=raw["dependencies"],
            )
            final = self._compute_final_score(raw, weights)
            results.append(PrioritizedRequirement(
                id=req.id,
                title=req.title,
                final_score=final,
                rank=0,  # assigned after sorting
                scores=dim_scores,
                reasoning=raw.get("reasoning", ""),
            ))

        results.sort(key=lambda r: r.final_score, reverse=True)
        for i, r in enumerate(results, start=1):
            r.rank = i

        return results
