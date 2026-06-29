from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.store import opportunities
from app.models.domain import Opportunity, ProjectType

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


class OpportunityCreate(BaseModel):
    title: str
    customer: str
    project_type: ProjectType
    submission_deadline: datetime | None = None


@router.post("", response_model=Opportunity, status_code=201)
def create_opportunity(payload: OpportunityCreate) -> Opportunity:
    opportunity = Opportunity(
        title=payload.title,
        customer=payload.customer,
        project_type=payload.project_type,
        submission_deadline=payload.submission_deadline,
    )
    return opportunities.put(opportunity.id, opportunity)


@router.get("", response_model=list[Opportunity])
def list_opportunities() -> list[Opportunity]:
    return opportunities.list()


@router.get("/{opportunity_id}", response_model=Opportunity)
def get_opportunity(opportunity_id: str) -> Opportunity:
    try:
        return opportunities.require(opportunity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Opportunity not found")
