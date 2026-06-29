# AI Tendering Assistant

An AI-driven co-pilot that accelerates tender management for DG Set (Diesel
Generator Set) and Balance of Plant (BOP) projects, while keeping a human
approver in the loop at every critical decision point.

## Scope of this implementation

This first slice is a FastAPI backend + workflow engine covering the tender
lifecycle:

1. **Opportunity intake** — register a tender opportunity, either manually
   or by converting a tender found by the multi-source discovery scan below.
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

## Tender discovery (multi-source monitoring)

`app/sources/` defines a `TenderSource` connector interface (mirroring the
LLM provider abstraction) with one implementation per approved platform:

- GeM
- CPPP/eProcure
- State Government Procurement Portals
- PSU Portals
- Railways
- Defence Portals

Each connector reads its own `*_API_BASE_URL` setting (see `app/core/config.py`)
and is skipped during a scan until that setting is provided — `GET
/discovery/sources` shows configured vs. unconfigured status per portal.
`POST /discovery/scan` polls every configured source and stores new results
(deduped by source + external ID) as `DiscoveredTender` records; it never
creates an `Opportunity` directly.

A human reviews `GET /discovery/tenders` and either:

- `POST /discovery/tenders/{id}/convert` — promotes it into a tracked
  `Opportunity` (entering the lifecycle above), or
- `POST /discovery/tenders/{id}/dismiss` — discards it.

**Wiring up a real portal**: each connector in `app/sources/portals.py` has
its base scaffolding (settings field, error handling, dedupe) in place, but
`_listing_path`/`_parse_listings` are intentionally `NotImplementedError`
stubs — each portal's actual search/listing API shape needs to be filled in
with that portal's real (documented, authorized) endpoint rather than a
guessed one. Implementing one is: fill in those two methods for the target
portal's connector class, then set its base URL env var.

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
  api/         FastAPI routers (opportunities, discovery, documents, bids, approvals, clarifications)
  core/        settings, in-memory store
  llm/         pluggable LLM provider abstraction + Claude implementation
  sources/     pluggable tender source connector abstraction + per-portal stubs
  models/      pydantic schemas / domain models
  services/    document parsing, analysis orchestration, discovery scan orchestration
  workflow/    tender lifecycle state machine + approval gate enforcement
```
