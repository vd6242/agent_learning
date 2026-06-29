from fastapi import APIRouter, HTTPException

from app.core.store import analyses, bid_drafts, opportunities
from app.llm.errors import LLMConfigurationError
from app.llm.factory import get_llm_provider
from app.models.domain import ApprovalStatus, BidDraft

router = APIRouter(tags=["bid-drafts"])

DRAFT_SYSTEM_PROMPT = """You are a bid-writing assistant for DG Set and BOP \
tenders. Draft a bid response using the approved tender analysis provided. \
The draft is a starting point for a human bid manager to revise -- it is not \
sent to the customer until that person approves it."""


@router.post("/opportunities/{opportunity_id}/bid-drafts", response_model=BidDraft, status_code=201)
async def create_bid_draft(opportunity_id: str) -> BidDraft:
    try:
        opportunities.require(opportunity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    approved_analyses = [
        a
        for a in analyses.list()
        if a.opportunity_id == opportunity_id and a.approval_status == ApprovalStatus.APPROVED
    ]
    if not approved_analyses:
        raise HTTPException(
            status_code=409,
            detail="No approved document analysis for this opportunity yet; "
            "a human must approve the analysis before drafting can start.",
        )

    analysis = approved_analyses[-1]
    user_content = (
        f"Tender summary: {analysis.summary}\n\n"
        f"Key requirements:\n" + "\n".join(f"- {r}" for r in analysis.key_requirements) + "\n\n"
        f"Eligibility criteria:\n" + "\n".join(f"- {c}" for c in analysis.eligibility_criteria)
    )

    try:
        llm = get_llm_provider()
        content = await llm.generate_text(system_prompt=DRAFT_SYSTEM_PROMPT, user_content=user_content)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    draft = BidDraft(opportunity_id=opportunity_id, content=content)
    return bid_drafts.put(draft.id, draft)


@router.get("/opportunities/{opportunity_id}/bid-drafts", response_model=list[BidDraft])
def list_bid_drafts(opportunity_id: str) -> list[BidDraft]:
    return [d for d in bid_drafts.list() if d.opportunity_id == opportunity_id]
