"""
prompts.py

Prompt templates for the requirement prioritization LLM calls.
"""

SCORING_PROMPT = """You are a senior product manager and software architect evaluating a software requirement.

Requirement:
Title: {title}
Description: {description}
Stakeholder Notes: {stakeholder_notes}
Dependencies: {dependencies}

Score this requirement on each of the following dimensions from 1 to 10:

1. business_value: How much does delivering this requirement directly impact business KPIs, revenue, or strategic goals? (1 = minimal impact, 10 = critical business driver)
2. stakeholder_priority: How urgently have stakeholders expressed the need for this? (1 = low urgency, 10 = blocking deals or critical stakeholders demanding it)
3. implementation_effort: How complex is the implementation? Invert the scale - score 10 if it is trivial, score 1 if it requires months of effort. (1 = enormous effort, 10 = quick win)
4. risk: What is the risk of NOT implementing this? (1 = no risk, 10 = severe risk to operations or customers)
5. dependencies: Does this unblock other work? (1 = isolated, 10 = many other requirements depend on this)

Respond in valid JSON only, with no markdown, no code blocks, exactly this structure:
{{
  "business_value": <float 1-10>,
  "stakeholder_priority": <float 1-10>,
  "implementation_effort": <float 1-10>,
  "risk": <float 1-10>,
  "dependencies": <float 1-10>,
  "reasoning": "<2-3 sentence explanation of why this requirement received these scores>"
}}
"""

DEFAULT_WEIGHTS = {
    "business_value": 0.30,
    "stakeholder_priority": 0.25,
    "implementation_effort": 0.15,
    "risk": 0.20,
    "dependencies": 0.10,
}
