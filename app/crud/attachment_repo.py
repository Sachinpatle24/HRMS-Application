# app/crud/attachment_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.attachment_model import Attachment

class AttachmentRepository:
    @staticmethod
    async def create(db: AsyncSession, attachment: Attachment) -> Attachment:
        db.add(attachment)
        return attachment

    @staticmethod
    async def get_by_candidate_id(db: AsyncSession, candidate_id: int) -> Optional[Attachment]:
        result = await db.execute(
            select(Attachment).where(Attachment.candidate_id == candidate_id)
        )
        return result.scalar_one_or_none()
