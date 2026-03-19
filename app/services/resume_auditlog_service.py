# app/services/resume_auditlog_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume_auditlog_model import ResumeAuditLog
from app.crud.resume_auditlog_repo import ResumeAuditLogRepository
from app.schemas.resume_auditlog_schema import ResumeAuditLogRead


class ResumeAuditLogService:

    @staticmethod
    async def create_log(
        db: AsyncSession,
        file_name: str,
        candidate_id: int | None = None,
        resume_status: bool = False,
        free_text: str | None = None
    ) -> ResumeAuditLog:
        """
        Create a new resume audit log (success/failure) entry.
        """
        log = ResumeAuditLog(
            candidate_id=candidate_id,
            file_name=file_name,
            resume_status=resume_status,
            free_text=free_text
        )
        await ResumeAuditLogRepository.create(db, log)
        return log

    @staticmethod
    async def get_log_by_candidate_id(
        db: AsyncSession,
        candidate_id: int
    ) -> Optional[ResumeAuditLog]:
        return await ResumeAuditLogRepository.get_by_candidate_id(db, candidate_id)

    @staticmethod
    async def list_logs(db: AsyncSession) -> List[ResumeAuditLog]:
        return await ResumeAuditLogRepository.list_all(db)
    
    @staticmethod
    async def list_failed_logs(db: AsyncSession) -> List[ResumeAuditLog]:
        return await ResumeAuditLogRepository.list_failed_logs(db)