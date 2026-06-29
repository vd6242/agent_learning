from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.store import discovered_tenders, opportunities
from app.models.domain import (
    DiscoveredTender,
    DiscoveryStatus,
    Opportunity,
    ProjectType,
    TenderSourceName,
)
from app.services.discovery_service import scan_sources
from app.sources.errors import SourceConfigurationError
from app.sources.factory import get_all_sources, get_enabled_sources

router = APIRouter(prefix="/discovery", tags=["discovery"])


class SourceStatus(BaseModel):
    source: TenderSourceName
    configured: bool


class ScanResult(BaseModel):
    new_tenders: list[DiscoveredTender]
    sources_scanned: list[TenderSourceName]
    sources_skipped_unconfigured: list[TenderSourceName]
    source_errors: dict[str, str]


class ConvertRequest(BaseModel):
    reviewer: str
    project_type: ProjectType | None = None


@router.get("/sources", response_model=list[SourceStatus])
def list_sources() -> list[SourceStatus]:
    enabled = {s.name for s in get_enabled_sources()}
    return [SourceStatus(source=s.name, configured=s.name in enabled) for s in get_all_sources()]


@router.post("/scan", response_model=ScanResult)
async def scan() -> ScanResult:
    all_sources = get_all_sources()
    enabled_sources = get_enabled_sources()
    enabled_names = {s.name for s in enabled_sources}

    new_tenders: list[DiscoveredTender] = []
    source_errors: dict[str, str] = {}
    for source in enabled_sources:
        try:
            new_tenders.extend(await scan_sources([source]))
        except SourceConfigurationError as exc:
            source_errors[source.name.value] = str(exc)
        except NotImplementedError as exc:
            source_errors[source.name.value] = f"connector not yet implemented: {exc}"

    return ScanResult(
        new_tenders=new_tenders,
        sources_scanned=[s.name for s in enabled_sources if s.name.value not in source_errors],
        sources_skipped_unconfigured=[s.name for s in all_sources if s.name not in enabled_names],
        source_errors=source_errors,
    )


@router.get("/tenders", response_model=list[DiscoveredTender])
def list_discovered_tenders(status: DiscoveryStatus | None = None) -> list[DiscoveredTender]:
    tenders = discovered_tenders.list()
    if status is not None:
        tenders = [t for t in tenders if t.status == status]
    return tenders


@router.post("/tenders/{tender_id}/dismiss", response_model=DiscoveredTender)
def dismiss_tender(tender_id: str) -> DiscoveredTender:
    try:
        tender = discovered_tenders.require(tender_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Discovered tender not found")
    tender.status = DiscoveryStatus.DISMISSED
    return tender


@router.post("/tenders/{tender_id}/convert", response_model=Opportunity, status_code=201)
def convert_tender(tender_id: str, payload: ConvertRequest) -> Opportunity:
    try:
        tender = discovered_tenders.require(tender_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Discovered tender not found")

    if tender.status == DiscoveryStatus.CONVERTED:
        raise HTTPException(status_code=409, detail="Tender already converted to an opportunity")

    project_type = payload.project_type or tender.project_type_guess
    if project_type is None:
        raise HTTPException(
            status_code=422,
            detail="project_type could not be inferred for this tender; specify it explicitly.",
        )

    opportunity = Opportunity(
        title=tender.title,
        customer=tender.organisation or tender.source.value,
        project_type=project_type,
        submission_deadline=tender.closing_date,
    )
    opportunities.put(opportunity.id, opportunity)

    tender.status = DiscoveryStatus.CONVERTED
    tender.converted_opportunity_id = opportunity.id

    return opportunity
