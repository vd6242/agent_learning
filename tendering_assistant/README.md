# AI Tendering Assistant

An AI-driven co-pilot that accelerates tender management for DG Set (Diesel
Generator Set) and Balance of Plant (BOP) projects, while keeping a human
approver in the loop at every critical decision point.

## Scope of this implementation

This first slice is a FastAPI backend + workflow engine covering the tender
lifecycle:

1. **Opportunity intake** — register a tender opportunity.
2. **Document analysis** — upload an RFP/tender document (PDF/DOCX/text) and
   get a structured AI extraction: scope summary, key requirements, eligibility
   criteria, deadlines, BOQ items relevant to DG Set/BOP, and risk flags.
3. **Approval gates** — every AI-produced artifact (analysis, draft bid,
   clarification response) is created in `pending_review` state and must be
   explicitly approved or rejected by a human before the workflow advances.
4. **Bid drafting** (stub) — scaffolding for AI-assisted draft generation,
   gated by approval.
5. **Clarification tracking** (stub) — scaffolding for logging and answering
   post-bid clarification questions, gated by approval.
6. **Submission** (stub) — marks a tender as submitted once all gates upstream
   are approved.

No frontend yet — everything is exposed over a REST API.

## LLM provider

AI features are called through a pluggable `LLMProvider` interface
(`app/llm/base.py`). The default implementation (`app/llm/anthropic_provider.py`)
uses the Claude API (`claude-opus-4-8` by default). Swapping providers is a
matter of implementing the same interface and pointing `LLM_PROVIDER` at it —
no other code changes.

Set `ANTHROPIC_API_KEY` in the environment to use the Claude provider. Without
a key configured, the app still runs; document-analysis calls will fail with a
clear configuration error until a key (or another provider) is supplied.

## Running

```bash
cd tendering_assistant
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs at `http://localhost:8000/docs`.

## Project layout

```
app/
  api/         FastAPI routers (opportunities, documents, bids, approvals, clarifications)
  core/        settings, in-memory store
  llm/         pluggable LLM provider abstraction + Claude implementation
  models/      pydantic schemas / domain models
  services/    document parsing, analysis orchestration
  workflow/    tender lifecycle state machine + approval gate enforcement
```
