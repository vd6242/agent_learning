from app.llm.base import LLMProvider
from app.models.domain import BoqItem, DocumentAnalysis, RiskFlag, TenderDocument

SYSTEM_PROMPT = """You are a tendering analyst supporting a team that bids on \
Diesel Generator (DG) Set and Balance of Plant (BOP) projects. You are given \
the full text of a tender/RFP document. Extract a structured analysis for a \
human reviewer who will approve or correct it before it is used.

Be conservative: only include requirements, deadlines, and BOQ items that are \
explicitly stated in the document. Flag anything ambiguous, unusually risky, \
or non-standard (e.g. onerous penalty clauses, short timelines, unusual \
warranty/performance bond terms) as a risk with a severity rating."""

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "2-4 sentence summary of the tender scope"},
        "key_requirements": {"type": "array", "items": {"type": "string"}},
        "eligibility_criteria": {"type": "array", "items": {"type": "string"}},
        "deadlines": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Each entry describes the event and date/timeframe, e.g. 'Bid submission: 2026-08-15'",
        },
        "boq_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "string"},
                    "unit": {"type": "string"},
                    "category": {
                        "type": "string",
                        "description": "e.g. DG Set, BOP, Civil, Electrical, Mechanical",
                    },
                },
                "required": ["description"],
            },
        },
        "risk_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "description": {"type": "string"},
                    "related_clause": {"type": "string"},
                },
                "required": ["severity", "description"],
            },
        },
    },
    "required": [
        "summary",
        "key_requirements",
        "eligibility_criteria",
        "deadlines",
        "boq_items",
        "risk_flags",
    ],
}


async def analyze_document(document: TenderDocument, llm: LLMProvider) -> DocumentAnalysis:
    result = await llm.extract_structured(
        system_prompt=SYSTEM_PROMPT,
        user_content=document.text,
        json_schema=ANALYSIS_SCHEMA,
        schema_name="tender_document_analysis",
    )
    return DocumentAnalysis(
        document_id=document.id,
        opportunity_id=document.opportunity_id,
        summary=result["summary"],
        key_requirements=result["key_requirements"],
        eligibility_criteria=result["eligibility_criteria"],
        deadlines=result["deadlines"],
        boq_items=[BoqItem(**item) for item in result["boq_items"]],
        risk_flags=[RiskFlag(**item) for item in result["risk_flags"]],
    )
