import io

from docx import Document as DocxDocument
from pypdf import PdfReader

SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def extract_text(content: bytes, content_type: str, filename: str) -> str:
    if content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = DocxDocument(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    if content_type == "text/plain":
        return content.decode("utf-8", errors="replace")

    raise ValueError(
        f"Unsupported content type '{content_type}' for file '{filename}'. "
        f"Supported: {sorted(SUPPORTED_CONTENT_TYPES)}"
    )
