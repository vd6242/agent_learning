"""Approval-gate enforcement.

Every AI-produced artifact (DocumentAnalysis, BidDraft, Clarification) is
created with approval_status=PENDING_REVIEW and the workflow stage only
advances once a human reviewer calls the approval endpoint. This module is
the single place that enforces "no AI output moves the tender forward
without an explicit human decision."
"""
from app.models.domain import ApprovalDecision, ApprovalStatus, Opportunity, TenderStage


class ApprovalGateError(Exception):
    pass


def apply_decision(approval_status: ApprovalStatus, decision: ApprovalDecision) -> ApprovalStatus:
    if approval_status != ApprovalStatus.PENDING_REVIEW:
        raise ApprovalGateError(
            f"Artifact already resolved with status '{approval_status}'; cannot re-decide."
        )
    return decision.decision


def advance_stage_on_approval(opportunity: Opportunity, from_stage: TenderStage, to_stage: TenderStage) -> Opportunity:
    if opportunity.stage != from_stage:
        raise ApprovalGateError(
            f"Opportunity '{opportunity.id}' is in stage '{opportunity.stage}', "
            f"expected '{from_stage}' before advancing to '{to_stage}'."
        )
    opportunity.stage = to_stage
    return opportunity
