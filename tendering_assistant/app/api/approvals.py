from fastapi import APIRouter, HTTPException

from app.core.store import analyses, bid_drafts, clarifications, opportunities
from app.models.domain import ApprovalDecision, TenderStage
from app.workflow.gates import ApprovalGateError, advance_stage_on_approval, apply_decision

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/analyses/{analysis_id}")
def decide_analysis(analysis_id: str, decision: ApprovalDecision) -> dict:
    try:
        analysis = analyses.require(analysis_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        analysis.approval_status = apply_decision(analysis.approval_status, decision)
    except ApprovalGateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    opportunity = opportunities.require(analysis.opportunity_id)
    if decision.decision.value == "approved" and opportunity.stage == TenderStage.DOCUMENT_ANALYSIS:
        advance_stage_on_approval(opportunity, TenderStage.DOCUMENT_ANALYSIS, TenderStage.BID_DRAFTING)

    return {"analysis": analysis, "opportunity_stage": opportunity.stage}


@router.post("/bid-drafts/{draft_id}")
def decide_bid_draft(draft_id: str, decision: ApprovalDecision) -> dict:
    try:
        draft = bid_drafts.require(draft_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Bid draft not found")

    try:
        draft.approval_status = apply_decision(draft.approval_status, decision)
    except ApprovalGateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    opportunity = opportunities.require(draft.opportunity_id)
    if decision.decision.value == "approved" and opportunity.stage == TenderStage.BID_DRAFTING:
        advance_stage_on_approval(opportunity, TenderStage.BID_DRAFTING, TenderStage.SUBMITTED)

    return {"bid_draft": draft, "opportunity_stage": opportunity.stage}


@router.post("/clarifications/{clarification_id}")
def decide_clarification(clarification_id: str, decision: ApprovalDecision) -> dict:
    try:
        clarification = clarifications.require(clarification_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Clarification not found")

    try:
        clarification.approval_status = apply_decision(clarification.approval_status, decision)
    except ApprovalGateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    return {"clarification": clarification}
