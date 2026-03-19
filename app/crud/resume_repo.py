from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, String, case, literal_column
from typing import Optional
from app.models.resume_model import Resume
from app.models.job.job_candidates_model import JobCandidate
from app.schemas.resume_schema import ResumeCreate, ResumeUpdate, ResumeConfirmationPayload, CandidateSearchWithStatusResponse


class ResumeRepository:
    @staticmethod
    async def count_all(db: AsyncSession, complete_only: bool = False) -> int:
        query = select(func.count()).select_from(Resume).where(Resume.active == True)
        if complete_only:
            query = query.where(Resume.is_complete == True)
        result = await db.execute(query)
        return result.scalar()

    @staticmethod
    async def list_resumes(db: AsyncSession, job_id: Optional[int], skip: int, limit: int, complete_only: bool):
        add_remove = case(
            (JobCandidate.candidate_id.isnot(None), 1), else_=0
        ).label("AddOrRemove") if job_id else literal_column("0").label("AddOrRemove")

        priority = case(
            (JobCandidate.candidate_id.isnot(None), 0), else_=1
        ) if job_id else None

        stmt = select(
            Resume.id, Resume.name, Resume.total_experience, Resume.total_experience_pretty,
            Resume.skills, Resume.phone, Resume.email, Resume.address, Resume.file_name,
            add_remove,
        ).where(Resume.active == True)

        if complete_only:
            stmt = stmt.where(Resume.is_complete == True)

        if job_id:
            stmt = stmt.outerjoin(
                JobCandidate,
                (JobCandidate.candidate_id == Resume.id) & (JobCandidate.job_id == job_id) & (JobCandidate.is_active == True),
            )
            stmt = stmt.order_by(priority, Resume.created_at.desc())
        else:
            stmt = stmt.order_by(Resume.created_at.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        rows = [dict(r._mapping) for r in result.all()]

        # Count
        count_stmt = select(func.count()).select_from(Resume).where(Resume.active == True)
        if complete_only:
            count_stmt = count_stmt.where(Resume.is_complete == True)
        if job_id:
            count_stmt = (
                select(func.count())
                .select_from(Resume)
                .outerjoin(
                    JobCandidate,
                    (JobCandidate.candidate_id == Resume.id) & (JobCandidate.job_id == job_id) & (JobCandidate.is_active == True),
                )
                .where(Resume.active == True)
            )
            if complete_only:
                count_stmt = count_stmt.where(Resume.is_complete == True)

        total_count = await db.scalar(count_stmt)

        return CandidateSearchWithStatusResponse(candidates=rows, total_candidates=total_count)

    @staticmethod
    async def search_candidates(db, query: str, job_id: Optional[int], skip: int, limit: Optional[int]):
        pattern = f"%{query.lower()}%"

        add_remove = case(
            (JobCandidate.candidate_id.isnot(None), 1), else_=0
        ).label("AddOrRemove") if job_id else literal_column("0").label("AddOrRemove")

        priority = case(
            (JobCandidate.candidate_id.isnot(None), 0), else_=1
        ) if job_id else None

        search_filter = or_(
            func.lower(func.coalesce(Resume.name, "")).like(pattern),
            func.lower(func.coalesce(Resume.skills, "")).like(pattern),
            cast(Resume.total_experience, String).like(f"%{query}%"),
            func.lower(func.coalesce(Resume.total_experience_pretty, "")).like(pattern),
        )

        stmt = select(
            Resume.id, Resume.name, Resume.total_experience, Resume.total_experience_pretty,
            Resume.skills, Resume.phone, Resume.email, Resume.address, Resume.file_name,
            add_remove,
        ).where(Resume.active == True, search_filter)

        if job_id:
            stmt = stmt.outerjoin(
                JobCandidate,
                (JobCandidate.candidate_id == Resume.id) & (JobCandidate.job_id == job_id) & (JobCandidate.is_active == True),
            )
            stmt = stmt.order_by(priority, Resume.created_at.desc())
        else:
            stmt = stmt.order_by(Resume.created_at.desc())

        if limit and limit > 0:
            stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        rows = [dict(r._mapping) for r in result.all()]

        # Count
        count_stmt = select(func.count()).select_from(Resume).where(Resume.active == True, search_filter)
        if job_id:
            count_stmt = (
                select(func.count())
                .select_from(Resume)
                .outerjoin(
                    JobCandidate,
                    (JobCandidate.candidate_id == Resume.id) & (JobCandidate.job_id == job_id) & (JobCandidate.is_active == True),
                )
                .where(Resume.active == True, search_filter)
            )

        total_count = await db.scalar(count_stmt)

        return CandidateSearchWithStatusResponse(candidates=rows, total_candidates=total_count)

    @staticmethod
    async def get_by_id(db: AsyncSession, candidate_id: int) -> Optional[Resume]:
        result = await db.execute(select(Resume).where(Resume.id == candidate_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, payload: ResumeCreate) -> Resume:
        resume_data = payload.model_dump(exclude_none=True)
        resume = Resume(**resume_data)
        db.add(resume)
        return resume

    @staticmethod
    async def update(db: AsyncSession, candidate_id: int, payload: ResumeUpdate) -> Optional[Resume]:
        result = await db.execute(select(Resume).where(Resume.id == candidate_id))
        resume = result.scalar_one_or_none()
        if not resume:
            return None
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resume, field, value)
        return resume

    @staticmethod
    async def confirm_update(db: AsyncSession, candidate_id: int, payload: ResumeConfirmationPayload) -> Optional[Resume]:
        result = await db.execute(select(Resume).where(Resume.id == candidate_id))
        resume = result.scalar_one_or_none()
        if not resume:
            return None
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(resume, field) and getattr(resume, field) != value:
                setattr(resume, field, value)
        return resume

    @staticmethod
    async def delete(db: AsyncSession, candidate_id: int) -> bool:
        result = await db.execute(select(Resume).where(Resume.id == candidate_id))
        resume = result.scalar_one_or_none()
        if not resume:
            return False
        resume.active = False
        return True

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Resume]:
        result = await db.execute(select(Resume).where(Resume.email == email))
        return result.scalar_one_or_none()
