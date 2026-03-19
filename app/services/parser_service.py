# app/services/parser_service.py

from typing import Dict
import asyncio
from fastapi import HTTPException

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_custom_logger
from app.core.config import settings
from app.services.resume_service import ResumeService
from app.services.resume_auditlog_service import ResumeAuditLogService

from app.utils.extract_text import clean_resume_text, extract_text_from_bytes

logger = get_custom_logger(app_name="parser_service")

SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".doc")


async def _call_parser_api(text: str) -> Dict:
    payload = {
        "resume_object": {
            "name": "name", "phoneNumbers": "phoneNumbers",
            "websites": "websites", "emails": "emails",
            "dateOfBirth": "dateOfBirth", "addresses": "addresses",
            "summary": "summary", "education": "education",
            "workExperience": "workExperience", "skills": "skills",
            "certifications": "certifications", "projects": "projects"
        },
        "resume_text": text
    }
    for attempt in range(2):
        try:
            timeout = httpx.Timeout(60, read=60.0, connect=30.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(settings.PARSE_API_ENDPOINT, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning(f"ML API attempt {attempt+1}/2 failed: {exc}")
            if attempt == 1:
                raise RuntimeError("Parser API error") from exc
            await asyncio.sleep(2 ** (attempt + 1))


async def _log_failure(db: AsyncSession, file_name: str, error: Exception):
    """Helper to log failed ingestion attempts after rollback."""
    try:
        await ResumeAuditLogService.create_log(
            db=db,
            candidate_id=None,
            file_name=file_name,
            resume_status=False,
            free_text=str(error)
        )
        await db.commit()
    except Exception as log_exc:
        logger.error(f"Failed to create audit log for {file_name}: {log_exc}")


class ParserService:

    @staticmethod
    async def parse_and_ingest_binary(
        db: AsyncSession,
        file_data: bytes,
        file_name: str,
        file_type: str,
        created_by: int
    ):

        logger.info(f"Ingesting binary resume: {file_name}")
        raw_text = extract_text_from_bytes(file_data, file_type)
        raw_text = clean_resume_text(raw_text)
        
        if raw_text is None:
            raise ValueError(f"Unsupported file type for {file_name}")
        if not raw_text.strip():
            raise ValueError(f"No extractable text (scanned/image-only or corrupted file) for {file_name}")
        
        try: 
            parsed_data = await _call_parser_api(raw_text)
            
            logger.info("PARSED success=%s", parsed_data.get("success"))
            
            if not parsed_data.get("success"):
                raise ValueError(f"Parser failed: {parsed_data.get('error', 'Unknown error')}")
            
            parsed_data["raw_text"] = raw_text

        except (RuntimeError, ValueError) as e:
            logger.error(f"Parser API failure for {file_name}: {str(e)}")
            await _log_failure(db, file_name, e)
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Parser service unavailable",
                    "message": "The resume parsing service is currently unreachable. Please try again later.",
                    "filename": file_name
                }
            )

        parsed_data.update({
            "file_name": file_name,
            "file_type": file_type,
            "file_data": file_data,
            "created_by": created_by
        })

        try:
            resume, _ = await ResumeService.create_resume_from_parser(db, parsed_data, replace=settings.REPLACE_EXISTING)

            await ResumeAuditLogService.create_log(
                db=db,
                candidate_id=resume.id,
                file_name=file_name,
                resume_status=True,
                free_text=None
            )
            await db.commit()

            if _.get("deduplication") == "skipped_existing":
                logger.info("Resume already exists — skipping downstream actions")
            elif _.get("deduplication") == "updated_existing":
                logger.info("Resume already exists — updating with downstream actions")
            else:
                logger.info(f"Resume ingested successfully: ID={resume.id}")
            return resume, _
        
        except HTTPException as e:
            await db.rollback()
            await _log_failure(db, file_name, e)
            raise 
