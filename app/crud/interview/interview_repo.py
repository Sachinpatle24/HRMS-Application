from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func
from typing import Optional, List, Dict, Any
from datetime import date, time
from app.models.interview.interview_model import Interview
from app.models.job.job_candidates_model import JobCandidate
from app.models.job.job_model import Job
from app.models.resume_model import Resume
from app.models.dropdown.dropdown_model import MasterDropdown


class InterviewRepository:

    @staticmethod
    async def get_candidates_by_job_id(db: AsyncSession, job_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(
                JobCandidate.id.label("job_candidate_id"),
                JobCandidate.job_id,
                JobCandidate.candidate_id,
                Resume.name,
                Resume.email,
                Resume.phone,
                Resume.designation,
                Resume.total_experience,
                Resume.skills,
                JobCandidate.current_stage_id,
                JobCandidate.current_result_id,
            )
            .join(Job, JobCandidate.job_id == Job.id)
            .join(Resume, JobCandidate.candidate_id == Resume.id)
            .where(JobCandidate.job_id == job_id, JobCandidate.is_active == True)
        )
        result = await db.execute(stmt)
        return [dict(r._mapping) for r in result.all()]

    @staticmethod
    async def check_job_id(db: AsyncSession, job_id: int) -> bool:
        result = await db.execute(select(Job.id).where(Job.id == job_id, Job.is_active == True))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_candidate_interview_history(
        db: AsyncSession, candidate_id: int, job_id: Optional[int] = None
    ) -> list[dict]:
        stmt = (
            select(
                Interview.id.label("interview_id"),
                Interview.stage_id,
                MasterDropdown.value_text.label("stage_name"),
                Interview.interviewer_id,
                Interview.interviewer_name,
                Interview.scheduled_interview_date,
                Interview.rating_id,
                Interview.result_id,
                Interview.status,
                Interview.comments,
                case((Interview.upload_feedback_template.isnot(None), 1), else_=0).label("has_feedback_file"),
                Interview.feedback_filename,
            )
            .outerjoin(MasterDropdown, Interview.stage_id == MasterDropdown.id)
            .where(Interview.candidate_id == candidate_id, Interview.active == True)
        )
        if job_id is not None:
            stmt = stmt.where(Interview.job_id == job_id)
        stmt = stmt.order_by(Interview.created_at.desc())
        result = await db.execute(stmt)
        return [dict(r._mapping) for r in result.all()]

    @staticmethod
    async def get_interview_details(db: AsyncSession, interview_id: int | None = None) -> List[Dict[str, Any]]:
        result_dropdown = MasterDropdown.__table__.alias("result_dropdown")
        stmt = (
            select(
                Interview.id.label("interview_id"),
                Interview.job_id,
                Interview.job_candidate_id,
                Interview.candidate_id,
                Resume.name.label("candidate_name"),
                Resume.designation,
                Interview.scheduled_interview_date,
                Interview.scheduled_start_time,
                Interview.scheduled_end_time,
                Interview.duration_id,
                Interview.stage_id,
                Interview.interviewer_id,
                Interview.is_interviewer_external,
                Interview.interviewer_name,
                Interview.interviewer_email_id,
                Interview.interview_mode_id,
                Interview.location,
                Interview.video_call_link,
                Interview.additional_notes,
                Interview.status,
                Interview.created_by,
                Interview.created_at,
                Interview.updated_at,
                Interview.result_id,
                result_dropdown.c.value_text.label("result_name"),
            )
            .join(Resume, Interview.candidate_id == Resume.id)
            .join(Job, Interview.job_id == Job.id)
            .outerjoin(result_dropdown, Interview.result_id == result_dropdown.c.id)
        )
        if interview_id is None:
            stmt = stmt.where(Interview.active == True).order_by(Interview.created_at.desc())
        else:
            stmt = stmt.where(Interview.id == interview_id)

        result = await db.execute(stmt)
        rows = result.all()
        return [dict(r._mapping) for r in rows] if rows else None

    @staticmethod
    async def get_interview_details_by_candidate_id(db: AsyncSession, candidate_id: int) -> list[dict]:
        stmt = (
            select(
                Interview.id.label("interview_id"),
                Interview.job_id,
                Interview.job_candidate_id,
                Interview.candidate_id,
                Resume.name.label("candidate_name"),
                Resume.designation,
                Interview.scheduled_interview_date,
                Interview.scheduled_start_time,
                Interview.scheduled_end_time,
                Interview.duration_id,
                Interview.stage_id,
                Interview.interviewer_id,
                Interview.is_interviewer_external,
                Interview.interviewer_name,
                Interview.interviewer_email_id,
                Interview.interview_mode_id,
                Interview.location,
                Interview.video_call_link,
                Interview.additional_notes,
                Interview.status,
                Interview.created_by,
                Interview.created_at,
                Interview.updated_at,
                Interview.result_id,
            )
            .join(Resume, Interview.candidate_id == Resume.id)
            .where(Interview.candidate_id == candidate_id, Interview.active == True)
            .order_by(Interview.created_at.desc())
        )
        result = await db.execute(stmt)
        return [dict(r._mapping) for r in result.all()]

    @staticmethod
    async def schedule_interview(
        db: AsyncSession,
        interview_id: Optional[int],
        job_id: int,
        job_candidate_id: int,
        candidate_id: int,
        stage_id: int,
        scheduled_interview_date: date,
        scheduled_start_time: time,
        scheduled_end_time: Optional[time],
        duration_id: int,
        is_interviewer_external: bool,
        interviewer_id: str,
        interviewer_name: str,
        interviewer_email_id: str,
        interview_mode_id: int,
        location: Optional[str],
        video_call_link: Optional[str],
        additional_notes: str,
        status: str,
        created_by: int,
        active: bool,
        template_id: Optional[int] = None,
    ) -> int:
        if interview_id is not None:
            interview = await db.get(Interview, interview_id)
            if interview:
                interview.job_id = job_id
                interview.job_candidate_id = job_candidate_id
                interview.candidate_id = candidate_id
                interview.stage_id = stage_id
                interview.scheduled_interview_date = scheduled_interview_date
                interview.scheduled_start_time = scheduled_start_time
                interview.scheduled_end_time = scheduled_end_time
                interview.duration_id = duration_id
                interview.is_interviewer_external = is_interviewer_external
                interview.interviewer_id = interviewer_id
                interview.interviewer_name = interviewer_name
                interview.interviewer_email_id = interviewer_email_id
                interview.interview_mode_id = interview_mode_id
                interview.location = location
                interview.video_call_link = video_call_link
                interview.additional_notes = additional_notes
                interview.status = status
                interview.active = active
                await db.flush()
                return interview.id

        interview = Interview(
            job_id=job_id,
            job_candidate_id=job_candidate_id,
            candidate_id=candidate_id,
            stage_id=stage_id,
            scheduled_interview_date=scheduled_interview_date,
            scheduled_start_time=scheduled_start_time,
            scheduled_end_time=scheduled_end_time,
            duration_id=duration_id,
            is_interviewer_external=is_interviewer_external,
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name,
            interviewer_email_id=interviewer_email_id,
            interview_mode_id=interview_mode_id,
            location=location,
            video_call_link=video_call_link,
            additional_notes=additional_notes,
            status=status,
            created_by=created_by,
            active=active,
        )
        db.add(interview)
        await db.flush()
        return interview.id
