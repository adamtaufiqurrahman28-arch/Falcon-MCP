from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.document_context import build_document_summary_prompt
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService


router = APIRouter(prefix="/api/document", tags=["document"])

document_service = DocumentService()
llm_service = LLMService()


@router.post("/summarize")
async def summarize_document(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    mode: str = Form(default="executive"),
    instruction: str | None = Form(default=None),
    max_chars: int = Form(default=60000),
):
    """
    Upload / input dokumen -> LLM memahami struktur dokumen
    -> summarize / extract insight -> output ringkasan PM yang rapi.

    Modes:
    - executive
    - technical
    - action_items
    - risk
    - section
    - customer_ready
    - business_insight
    """
    if not llm_service.is_ready():
        raise HTTPException(
            status_code=400,
            detail="LLM belum siap. Cek LLM_API_KEY, LLM_BASE_URL, dan LLM_MODEL.",
        )

    if not file and not text:
        raise HTTPException(
            status_code=400,
            detail="Upload file atau isi text input terlebih dahulu.",
        )

    try:
        if file:
            extracted = await document_service.extract_from_upload(file)
        else:
            extracted = document_service.extract_from_text(text or "")

        compact = document_service.compact_document_for_llm(
            extracted.text,
            max_chars=max_chars,
        )

        prompt = build_document_summary_prompt(
            document_text=compact["text"],
            filename=extracted.filename,
            mode=mode,
            user_instruction=instruction,
            metadata={
                "extension": extracted.extension,
                "char_count": extracted.char_count,
                "chunk_count": extracted.chunk_count,
                "is_truncated": compact["is_truncated"],
            },
        )

        summary = llm_service.generate(prompt, temperature=0.2)

        return {
            "filename": extracted.filename,
            "extension": extracted.extension,
            "mode": mode,
            "char_count": extracted.char_count,
            "chunk_count": extracted.chunk_count,
            "is_truncated": compact["is_truncated"],
            "summary": summary,
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/modes")
async def document_summary_modes():
    return {
        "modes": [
            {"value": "executive", "label": "Executive Summary"},
            {"value": "technical", "label": "Technical Summary"},
            {"value": "action_items", "label": "Action Items"},
            {"value": "risk", "label": "Risk Register"},
            {"value": "section", "label": "Section Summary"},
            {"value": "customer_ready", "label": "Customer Ready Narrative"},
            {"value": "business_insight", "label": "Business Insight"},
        ]
    }
