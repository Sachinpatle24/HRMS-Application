# app/crud/resume_auditlog_repo.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.resume_auditlog_model import ResumeAuditLog


class ResumeAuditLogRepository:

    @staticmethod
    async def create(db: AsyncSession, entity: ResumeAuditLog) -> ResumeAuditLog:
        db.add(entity)
        return entity

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[ResumeAuditLog]:
        result = await db.execute(
            select(ResumeAuditLog).where(ResumeAuditLog.id == log_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_candidate_id(
        db: AsyncSession, candidate_id: int
    ) -> Optional[ResumeAuditLog]:
        result = await db.execute(
            select(ResumeAuditLog).where(ResumeAuditLog.candidate_id == candidate_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> List[ResumeAuditLog]:
        result = await db.execute(select(ResumeAuditLog))
        return result.scalars().all()
    
    @staticmethod
    async def list_failed_logs(db: AsyncSession) -> List[ResumeAuditLog]:
        result = await db.execute(
            select(ResumeAuditLog).where(ResumeAuditLog.resume_status == False)
        )
        return result.scalars().all()
