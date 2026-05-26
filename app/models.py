"""
models.py

Pydantic models for API request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str = Field(..., description="Unique requirement identifier, e.g. REQ-001")
    title: str = Field(..., description="Short descriptive title")
    description: str = Field(..., description="Detailed requirement description")
    stakeholder_notes: Optional[str] = Field(
        default=None, description="Any stakeholder context or urgency notes"
    )
    dependencies: Optional[List[str]] = Field(
        default=None, description="List of requirement IDs this one depends on"
    )


class DimensionScores(BaseModel):
    business_value: float = Field(..., ge=1, le=10)
    stakeholder_priority: float = Field(..., ge=1, le=10)
    implementation_effort: float = Field(..., ge=1, le=10,
        description="Effort score (10 = low effort, 1 = very high effort)")
    risk: float = Field(..., ge=1, le=10)
    dependencies: float = Field(..., ge=1, le=10)


class PrioritizedRequirement(BaseModel):
    id: str
    title: str
    final_score: float = Field(..., description="Weighted priority score (higher = more urgent)")
    rank: int
    scores: DimensionScores
    reasoning: str = Field(..., description="LLM-generated justification for the score")


class PrioritizeRequest(BaseModel):
    requirements: List[Requirement] = Field(..., min_items=1, max_items=50)
    weights: Optional[dict] = Field(
        default=None,
        description="Custom weights for scoring dimensions. Keys: business_value, "
                    "stakeholder_priority, implementation_effort, risk, dependencies"
    )


class PrioritizeResponse(BaseModel):
    results: List[PrioritizedRequirement]
    model_used: str
    total_requirements: int
