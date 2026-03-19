from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json

from app.models.resume_model import Resume
from app.schemas.resume_schema import ResumeCreate, ResumeUpdate, ResumeConfirmationPayload, CandidateSearchWithStatusResponse
from app.crud.resume_repo import ResumeRepository
from app.core.logger import get_custom_logger

from app.services.parser_normalizer import normalize_parser_output, safe_json_dumps
from app.services.resume_validator import validate_resume_for_search, build_completeness_payload

from app.services.attachment_service import AttachmentService
from app.schemas.attachment_schema import AttachmentCreate

from app.services.candidate_rawdata_service import CandidateRawDataService
from app.schemas.candidate_rawdata_schema import CandidateRawDataCreate

from app.services.resume_auditlog_service import ResumeAuditLogService

from app.services.experience_service import (
    format_decimal_experience,
    calculate_total_experience,
    format_total_experience_string,
    calculate_experience_per_company,
)

logger = get_custom_logger(app_name="resume_service")

class ResumeService:

    @staticmethod
    async def count_resumes(
        db: AsyncSession, 
        complete_only: bool = False
    ) -> int:
        return await ResumeRepository.count_all(db, complete_only)

    @staticmethod
    async def list_resumes(
        db: AsyncSession,
        job_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
        complete_only: bool = False
    ) -> CandidateSearchWithStatusResponse:
        logger.info(f"Fetching resumes: skip={skip}, limit={limit}, complete_only={complete_only}")
        return await ResumeRepository.list_resumes(db, job_id, skip, limit, complete_only)

    @staticmethod
    async def search_candidates(
        db: AsyncSession,
        query: str,
        job_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> CandidateSearchWithStatusResponse:
        return await ResumeRepository.search_candidates(db, query, job_id, skip, limit)

    @staticmethod
    async def get_resume(
        db: AsyncSession,
        id: int
    ) -> Optional[Resume]:
        logger.info(f"Fetching resume with ID {id}")
        return await ResumeRepository.get_by_id(db, id)

    @staticmethod
    async def create_resume(
        db: AsyncSession,
        payload: ResumeCreate
    ) -> Resume:
        logger.info(f"Creating new resume entry for name={payload.name}")

        if payload.email:
            existing = await ResumeRepository.get_by_email(db, payload.email)
            if existing:
                raise ValueError(f"Resume with email {payload.email} already exists")
        
        resume = await ResumeRepository.create(db, payload)

        verification_payload = build_completeness_payload(resume)
        missing_fields = validate_resume_for_search(verification_payload)

        new_is_complete = not bool(missing_fields)
        if resume.is_complete != new_is_complete:
            resume.is_complete = new_is_complete
            
        await db.commit()
        await db.refresh(resume)

        await ResumeAuditLogService.create_log(
            db=db,
            candidate_id=resume.id,
            file_name=f"{resume.file_name}",
            resume_status=True,
            free_text="Manual resume creation via API"
        )
        await db.commit()

        return resume

    @staticmethod
    async def confirm_resume(
        resume_id: int,
        payload: ResumeConfirmationPayload,
        db: AsyncSession
    ) -> Resume:
        resume = await ResumeRepository.confirm_update(db, resume_id, payload)

        if not resume:
            raise ValueError("Resume not found")

        if payload.total_experience is not None:
            resume.total_experience_pretty = format_decimal_experience(
                payload.total_experience
            )

        verification_payload = build_completeness_payload(resume)
        missing_fields = validate_resume_for_search(verification_payload)

        new_is_complete = not bool(missing_fields)
        if resume.is_complete != new_is_complete:
            resume.is_complete = new_is_complete

        try:
            await db.commit()
            await db.refresh(resume)
            logger.info(f"Resume ID={resume_id} confirmed successfully")
        except Exception:
            await db.rollback()
            raise

        return resume

    @staticmethod
    async def update_resume(
        db: AsyncSession,
        id: int,
        payload: ResumeUpdate
    ):
        logger.info(f"Updating resume ID={id}")

        resume = await ResumeRepository.update(db, id, payload)

        if not resume:
            logger.warning(f"Resume ID={id} not found for update")
            return None
        
        try:
            await db.commit()
            await db.refresh(resume)
            logger.info(f"Resume ID={id} updated successfully")
        except Exception:
            await db.rollback()
            raise
        return resume

    @staticmethod
    async def delete_resume(
        db: AsyncSession,
        id: int
    ) -> bool:
        logger.info(f"Deleting resume ID={id}")

        success = await ResumeRepository.delete(db, id)
        if success:
            await db.commit()
            logger.info(f"Resume ID={id} deleted successfully")
        else:
            logger.warning(f"Resume ID={id} not found for deletion")

        return success

    @staticmethod
    async def create_resume_from_parser(
        db: AsyncSession,
        parsed_data: dict,
        replace: bool = False
    ):
        data = parsed_data.get("data")
        data_keys = list(data.keys()) if isinstance(data, dict) else None

        logger.info("data keys=%s", data_keys)
        logger.info("Creating resume from parsed ML output")
        
        normalized_data = normalize_parser_output(parsed_data)

        # Experience enrichment
        work_exp_raw = normalized_data.get("work_experience") or "[]"
        
        try:
            work_exp = json.loads(work_exp_raw) if isinstance(work_exp_raw, str) else work_exp_raw
        except (json.JSONDecodeError, TypeError):
            work_exp = []

        if isinstance(work_exp, list) and work_exp:
            normalized_data["total_experience"] = calculate_total_experience(work_exp)
            normalized_data["total_experience_pretty"] = format_total_experience_string(work_exp)

            per_company_dec, per_company_pretty = calculate_experience_per_company(work_exp)
            normalized_data["experience_per_company"] = json.dumps(per_company_dec)
            normalized_data["experience_per_company_pretty"] = json.dumps(per_company_pretty)
        else:
            normalized_data["total_experience"] = 0.0
            normalized_data["total_experience_pretty"] = "0 months"
            normalized_data["experience_per_company"] = json.dumps([])
            normalized_data["experience_per_company_pretty"] = json.dumps([])

        # Validation
        verification_payload = build_completeness_payload(normalized_data)
        missing_fields = validate_resume_for_search(verification_payload)

        if missing_fields:
            logger.warning(
                "Resume ingested with missing business fields",
                extra={"missing_fields": missing_fields}
            )

        # Email Deduplication
        email = normalized_data.get("email")
        
        if email:
            existing = await ResumeRepository.get_by_email(db, email)
            if existing:
                logger.info(
                    "Duplicate resume detected by email",
                    extra={"email": email, "id": str(existing.id)}
                )
                
                if replace:
                    for field, value in normalized_data.items():
                        if value is not None and field != "email":
                            setattr(existing, field, value)
                    
                    existing.is_complete = not bool(missing_fields)

                    await db.flush()
                    await db.refresh(existing)

                    raw_payload = CandidateRawDataCreate(
                        candidate_id=existing.id,
                        raw_text=parsed_data.get("raw_text"),
                        parsed_json=safe_json_dumps(parsed_data.get("data"), default={})
                    )

                    await CandidateRawDataService.upsert_raw_data(
                        db, payload=raw_payload, replace=True
                    )

                    file_data = parsed_data.get("file_data")
                    file_type = parsed_data.get("file_type")
                    file_name = parsed_data.get("file_name")

                    if file_data and file_type and file_name:
                        attachment_payload = AttachmentCreate(
                            candidate_id=existing.id,
                            file_name=file_name,
                            file_data=file_data,
                            file_type=file_type
                        )
                        await AttachmentService.upsert_attachment(
                            db, attachment_payload, replace_binary=True
                        )

                    try:
                        await db.commit()
                        await db.refresh(existing)
                    except Exception:
                        await db.rollback()
                        raise
                    
                    return existing, {**normalized_data, "deduplication": "replaced_existing"}
                
                else:
                    logger.warning(
                        "Duplicate resume upload ignored - keeping original",
                        extra={"email": email, "existing_id": str(existing.id)}
                    )
                    return existing, {
                        **normalized_data,
                        "deduplication": "skipped_existing",
                    }

        # Create new resume    
        payload = ResumeCreate(**normalized_data)
        logger.info(
            "NORMALIZED PAYLOAD = name=%s, email=%s, is_complete=%s",
            payload.name, payload.email, not bool(missing_fields)
        )
        resume = await ResumeRepository.create(db, payload)
        resume.is_complete = not bool(missing_fields)

        await db.flush()
        await db.refresh(resume)
        logger.info(f"Resume flushed with id={resume.id}")
        
        # Persist raw parser artifacts
        raw_payload = CandidateRawDataCreate(
            candidate_id=resume.id,
            raw_text=parsed_data.get("raw_text"),
            parsed_json=safe_json_dumps(parsed_data.get("data"), default={})
        )
        await CandidateRawDataService.upsert_raw_data(db, payload=raw_payload, replace=False)

        # Persist binary attachment
        file_data = parsed_data.get("file_data")
        file_type = parsed_data.get("file_type")
        file_name = parsed_data.get("file_name")

        if file_data and file_type and file_name: 
            attachment_payload = AttachmentCreate(
                candidate_id=resume.id,
                file_name=file_name,
                file_data=file_data,
                file_type=file_type
            )
            await AttachmentService.upsert_attachment(db, attachment_payload, replace_binary=False)

        try:
            await db.commit()
            await db.refresh(resume)
        except Exception:
            await db.rollback()
            raise

        return resume, {**normalized_data, "deduplication": "created_new"}
