import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ApprovalStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class TenderStage(StrEnum):
    OPPORTUNITY_IDENTIFIED = "opportunity_identified"
    DOCUMENT_ANALYSIS = "document_analysis"
    BID_DRAFTING = "bid_drafting"
    SUBMITTED = "submitted"
    CLARIFICATIONS = "clarifications"
    CLOSED = "closed"


class ProjectType(StrEnum):
    DG_SET = "dg_set"
    BOP = "bop"
    DG_SET_AND_BOP = "dg_set_and_bop"


class Opportunity(BaseModel):
    id: str = Field(default_factory=lambda: new_id("opp"))
    title: str
    customer: str
    project_type: ProjectType
    submission_deadline: datetime | None = None
    stage: TenderStage = TenderStage.OPPORTUNITY_IDENTIFIED
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TenderDocument(BaseModel):
    id: str = Field(default_factory=lambda: new_id("doc"))
    opportunity_id: str
    filename: str
    content_type: str
    text: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class BoqItem(BaseModel):
    description: str
    quantity: str | None = None
    unit: str | None = None
    category: str | None = None  # e.g. "DG Set", "BOP", "Civil", "Electrical"


class RiskFlag(BaseModel):
    severity: str  # "low" | "medium" | "high"
    description: str
    related_clause: str | None = None


class DocumentAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: new_id("analysis"))
    document_id: str
    opportunity_id: str
    summary: str
    key_requirements: list[str] = Field(default_factory=list)
    eligibility_criteria: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    boq_items: list[BoqItem] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BidDraft(BaseModel):
    id: str = Field(default_factory=lambda: new_id("draft"))
    opportunity_id: str
    content: str
    approval_status: ApprovalStatus = ApprovalStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Clarification(BaseModel):
    id: str = Field(default_factory=lambda: new_id("clar"))
    opportunity_id: str
    question: str
    proposed_response: str | None = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalDecision(BaseModel):
    decision: ApprovalStatus
    reviewer: str
    notes: str | None = None
