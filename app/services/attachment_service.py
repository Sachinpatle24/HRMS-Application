# app/services/attachment_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.attachment_repo import AttachmentRepository
from app.schemas.attachment_schema import AttachmentCreate
from app.models.attachment_model import Attachment
from app.core.logger import get_custom_logger

logger = get_custom_logger(app_name="attachment_service")


class AttachmentService:

    @staticmethod
    async def upsert_attachment(
        db: AsyncSession,
        payload: AttachmentCreate,
        *,
        replace_binary: bool = True
    ) -> Attachment:
        """
        One-to-one attachment semantics:
        - If attachment exists → update or skip binary
        - If not → create new attachment
        """

        attachment = await AttachmentRepository.get_by_candidate_id(
            db, payload.candidate_id
        )

        if attachment:
            logger.info(
                "Attachment exists for resume",
                extra={"candidate_id": payload.candidate_id},
            )

            if replace_binary:
                attachment.file_data = payload.file_data
                attachment.file_name = payload.file_name
                attachment.file_type = payload.file_type
        else:
            logger.info(
                "Creating new attachment",
                extra={"candidate_id": payload.candidate_id},
            )
            attachment = Attachment(
                **payload.model_dump(exclude_none=True)
            )
            db.add(attachment)

        try:
            await db.flush()
            await db.refresh(attachment)
        except Exception:
            await db.rollback()
            logger.exception("Failed to upsert attachment")
            raise

        return attachment

    @staticmethod
    async def get_attachment_for_resume(
        db: AsyncSession,
        resume_id: int
    ) -> Attachment | None:
        return await AttachmentRepository.get_by_candidate_id(db, resume_id)
