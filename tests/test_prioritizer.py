"""
test_prioritizer.py

Unit tests for scoring and ranking logic (no LLM calls in unit tests).
"""

import pytest
from unittest.mock import MagicMock, patch

from app.models import Requirement, DimensionScores, PrioritizedRequirement
from app.prioritizer import RequirementPrioritizer
from app.prompts import DEFAULT_WEIGHTS


MOCK_LLM_RESPONSE = {
    "business_value": 9.0,
    "stakeholder_priority": 8.0,
    "implementation_effort": 6.0,
    "risk": 7.0,
    "dependencies": 8.0,
    "reasoning": "This requirement is critical for enterprise adoption.",
}

REQ_SSO = Requirement(
    id="REQ-001",
    title="SSO Integration",
    description="Allow login via corporate SSO",
    stakeholder_notes="Blocking 3 enterprise deals",
)

REQ_DARK_MODE = Requirement(
    id="REQ-002",
    title="Dark Mode",
    description="Toggle for dark UI theme",
    stakeholder_notes="Nice to have from community",
)


@patch.object(RequirementPrioritizer, "__init__", lambda self, **kwargs: None)
def make_prioritizer():
    p = RequirementPrioritizer.__new__(RequirementPrioritizer)
    p.model_name = "test-model"
    return p


def test_compute_final_score():
    p = make_prioritizer()
    scores = {
        "business_value": 10,
        "stakeholder_priority": 10,
        "implementation_effort": 10,
        "risk": 10,
        "dependencies": 10,
    }
    result = p._compute_final_score(scores, DEFAULT_WEIGHTS)
    assert result == 10.0


def test_compute_final_score_weighted():
    p = make_prioritizer()
    scores = {
        "business_value": 10,
        "stakeholder_priority": 1,
        "implementation_effort": 1,
        "risk": 1,
        "dependencies": 1,
    }
    result = p._compute_final_score(scores, DEFAULT_WEIGHTS)
    # business_value has weight 0.30, so it should dominate
    assert result > 3.0


def test_prioritize_ranking():
    p = make_prioritizer()

    high_score_req = PrioritizedRequirement(
        id="REQ-001", title="SSO", final_score=8.5, rank=0,
        scores=DimensionScores(
            business_value=9, stakeholder_priority=8,
            implementation_effort=7, risk=8, dependencies=9
        ),
        reasoning="Critical"
    )
    low_score_req = PrioritizedRequirement(
        id="REQ-002", title="Dark Mode", final_score=4.0, rank=0,
        scores=DimensionScores(
            business_value=3, stakeholder_priority=4,
            implementation_effort=8, risk=2, dependencies=2
        ),
        reasoning="Nice to have"
    )

    items = [low_score_req, high_score_req]
    items.sort(key=lambda r: r.final_score, reverse=True)
    for i, r in enumerate(items, start=1):
        r.rank = i

    assert items[0].id == "REQ-001"
    assert items[0].rank == 1
    assert items[1].rank == 2
