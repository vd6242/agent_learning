from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.store import clarifications, opportunities
from app.llm.errors import LLMConfigurationError
from app.llm.factory import get_llm_provider
from app.models.domain import Clarification

router = APIRouter(tags=["clarifications"])

CLARIFICATION_SYSTEM_PROMPT = """You are assisting a tendering team with a \
post-bid clarification question raised by the customer. Propose a response. \
This is a suggestion only -- a human must review and approve it before it is \
sent to the customer."""


class ClarificationCreate(BaseModel):
    question: str


@router.post(
    "/opportunities/{opportunity_id}/clarifications",
    response_model=Clarification,
    status_code=201,
)
async def create_clarification(opportunity_id: str, payload: ClarificationCreate) -> Clarification:
    try:
        opportunities.require(opportunity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    try:
        llm = get_llm_provider()
        proposed_response = await llm.generate_text(
            system_prompt=CLARIFICATION_SYSTEM_PROMPT, user_content=payload.question
        )
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    clarification = Clarification(
        opportunity_id=opportunity_id,
        question=payload.question,
        proposed_response=proposed_response,
    )
    return clarifications.put(clarification.id, clarification)


@router.get("/opportunities/{opportunity_id}/clarifications", response_model=list[Clarification])
def list_clarifications(opportunity_id: str) -> list[Clarification]:
    return [c for c in clarifications.list() if c.opportunity_id == opportunity_id]
