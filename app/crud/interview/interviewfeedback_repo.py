from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from datetime import datetime, timezone
from app.models.interview.interview_model import Interview
from app.models.resume_model import Resume
from app.models.job.job_model import Job


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_interview_feedback(
        self,
        interview_id: int,
        comments: str | None,
        upload_feedback_template: bytes | None,
        feedback_filename: str | None,
        rating_id: int | None,
        result_id: int | None,
        rejection_id: int | None,
        feedback_at: datetime | None,
        active: bool | None,
        status: str | None,
    ):
        interview = await self.db.get(Interview, interview_id)
        if not interview:
            raise ValueError("Interview not found")

        if comments is not None:
            interview.comments = comments
        if upload_feedback_template is not None:
            interview.upload_feedback_template = upload_feedback_template
        if feedback_filename is not None:
            interview.feedback_filename = feedback_filename
        if rating_id is not None:
            interview.rating_id = rating_id
        if result_id is not None:
            interview.result_id = result_id
        if rejection_id is not None:
            interview.rejection_id = rejection_id
        interview.feedback_at = feedback_at or datetime.now(timezone.utc)
        if active is not None:
            interview.active = active
        if status is not None:
            interview.status = status

        await self.db.flush()
        return interview.id

    async def get_feedback_file(self, interview_id: int) -> dict | None:
        interview = await self.db.get(Interview, interview_id)
        if not interview:
            return None
        return {
            "id": interview.id,
            "file_bytes": interview.upload_feedback_template,
            "file_name": interview.feedback_filename,
        }

    async def get_feedback_page_by_interview(self, interview_id: int):
        stmt = (
            select(
                Interview.id.label("interview_id"),
                Interview.candidate_id,
                Resume.name.label("candidate_name"),
                Resume.email,
                Resume.phone,
                Resume.current_company,
                Resume.designation,
                Resume.total_experience,
                Resume.address,
                Resume.notice_period,
                Resume.last_working_day,
                Resume.skills,
                Interview.job_id,
                Job.title.label("position_title"),
                Job.mandatory_skills,
                Job.desired_skills,
                Job.qualification,
                Interview.scheduled_interview_date,
                Interview.scheduled_start_time,
                Interview.interviewer_id,
                Interview.is_interviewer_external,
                Interview.interviewer_name,
                Interview.interviewer_email_id,
                Interview.comments,
                Interview.feedback_filename,
                case((Interview.upload_feedback_template.isnot(None), 1), else_=0).label("has_feedback_file"),
                Interview.rating_id,
                Interview.result_id,
                Interview.rejection_id,
                Interview.feedback_at,
            )
            .join(Resume, Interview.candidate_id == Resume.id)
            .join(Job, Interview.job_id == Job.id)
            .where(Interview.id == interview_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            return None
        d = dict(row._mapping)
        d["template_id"] = None
        d["template_file_name"] = None
        return d
