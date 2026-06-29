from fastapi import FastAPI

from app.api import approvals, bid_drafts, clarifications, discovery, documents, opportunities

app = FastAPI(
    title="AI Tendering Assistant",
    description=(
        "Co-pilot for DG Set / BOP tender management. AI features assist at "
        "every stage; human approval gates every critical decision."
    ),
    version="0.1.0",
)

app.include_router(opportunities.router)
app.include_router(discovery.router)
app.include_router(documents.router)
app.include_router(approvals.router)
app.include_router(bid_drafts.router)
app.include_router(clarifications.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
