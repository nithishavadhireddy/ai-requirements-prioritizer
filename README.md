# ai-requirements-prioritizer

An LLM-powered REST API that automatically prioritises software requirements by evaluating
them against key decision factors: stakeholder preferences, business value, estimated effort,
risk, and inter-requirement dependencies.

Built with FastAPI and Hugging Face transformer models. Designed to reduce bias and manual
effort in the backlog prioritisation process.

## Motivation

Manual requirement prioritisation is slow, inconsistent, and often dominated by whoever speaks
loudest in the room. This tool applies a structured scoring framework via prompt engineering
and LLM reasoning to produce consistent, explainable priority scores.

## Architecture

```
Client  →  FastAPI  →  Prioritizer  →  HuggingFace LLM  →  Scored + Ranked Results
```

## Scoring Dimensions

Each requirement is scored 1-10 on:
- **Business Value** - impact on core KPIs or revenue
- **Stakeholder Priority** - urgency signalled by stakeholders
- **Implementation Effort** - estimated development complexity (inverse)
- **Risk** - technical or business risk if not addressed
- **Dependencies** - whether other requirements are blocked by this one

Final score: weighted average across dimensions.

## Setup

```bash
git clone https://github.com/<username>/ai-requirements-prioritizer
cd ai-requirements-prioritizer
pip install -r requirements.txt

# Set your HuggingFace token
cp .env.example .env
# Edit .env and add HUGGINGFACE_TOKEN=hf_...

# Start the server
uvicorn app.main:app --reload --port 8000
```

## API Usage

```bash
curl -X POST http://localhost:8000/prioritize \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": [
      {
        "id": "REQ-001",
        "title": "User authentication via SSO",
        "description": "Allow users to log in using their corporate SSO provider",
        "stakeholder_notes": "Requested by enterprise clients, blocking 3 deals"
      },
      {
        "id": "REQ-002",
        "title": "Dark mode UI",
        "description": "Add dark mode toggle to the web interface",
        "stakeholder_notes": "Requested by several community users"
      }
    ]
  }'
```

## Project Structure

```
ai-requirements-prioritizer/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── models.py        # Pydantic request/response models
│   ├── prioritizer.py   # LLM scoring logic
│   └── prompts.py       # Prompt templates
└── tests/
    └── test_prioritizer.py
```
