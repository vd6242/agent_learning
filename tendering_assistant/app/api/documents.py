from fastapi import APIRouter, HTTPException, UploadFile

from app.core.store import analyses, documents, opportunities
from app.llm.errors import LLMConfigurationError
from app.llm.factory import get_llm_provider
from app.models.domain import DocumentAnalysis, TenderDocument, TenderStage
from app.services.analysis_service import analyze_document
from app.services.document_parser import extract_text

router = APIRouter(tags=["documents"])


@router.post("/opportunities/{opportunity_id}/documents", response_model=TenderDocument, status_code=201)
async def upload_document(opportunity_id: str, file: UploadFile) -> TenderDocument:
    try:
        opportunities.require(opportunity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    content = await file.read()
    try:
        text = extract_text(content, file.content_type or "text/plain", file.filename or "upload")
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc))

    document = TenderDocument(
        opportunity_id=opportunity_id,
        filename=file.filename or "upload",
        content_type=file.content_type or "text/plain",
        text=text,
    )
    return documents.put(document.id, document)


@router.post("/documents/{document_id}/analyze", response_model=DocumentAnalysis, status_code=201)
async def analyze_uploaded_document(document_id: str) -> DocumentAnalysis:
    try:
        document = documents.require(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        llm = get_llm_provider()
        analysis = await analyze_document(document, llm)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    analyses.put(analysis.id, analysis)

    opportunity = opportunities.require(document.opportunity_id)
    if opportunity.stage == TenderStage.OPPORTUNITY_IDENTIFIED:
        opportunity.stage = TenderStage.DOCUMENT_ANALYSIS

    return analysis


@router.get("/opportunities/{opportunity_id}/analyses", response_model=list[DocumentAnalysis])
def list_analyses(opportunity_id: str) -> list[DocumentAnalysis]:
    return [a for a in analyses.list() if a.opportunity_id == opportunity_id]


@router.get("/analyses/{analysis_id}", response_model=DocumentAnalysis)
def get_analysis(analysis_id: str) -> DocumentAnalysis:
    try:
        return analyses.require(analysis_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Analysis not found")
