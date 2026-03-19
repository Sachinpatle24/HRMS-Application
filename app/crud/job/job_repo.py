from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime, timezone
from app.models.job.job_model import Job
from app.models.job.job_candidates_model import JobCandidate
from app.models.dropdown.dropdown_model import MasterDropdown
from app.models.user.users_model import User
from app.schemas.job.job_schema import JobRead, JobListRead


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_job_sp(
        self,
        id: int | None,
        title: str,
        number_of_positions: int,
        status_id: int,
        positions_filled: int | None,
        mandatory_skills: str | None,
        desired_skills: str | None,
        qualification: str | None,
        location: str | None,
        experience_level: str | None,
        job_description: str | None,
        department: str | None,
        is_active: bool,
        created_by: int,
        expires_at: datetime | None = None,
        assigned_to: int | None = None,
    ):
        if id is not None:
            job = await self.db.get(Job, id)
            if job:
                job.title = title
                job.number_of_positions = number_of_positions
                job.status_id = status_id
                job.positions_filled = positions_filled or 0
                job.mandatory_skills = mandatory_skills
                job.desired_skills = desired_skills
                job.qualification = qualification
                job.location = location
                job.experience_level = experience_level
                job.job_description = job_description
                job.department = department
                job.is_active = is_active
                job.expires_at = expires_at
                job.assigned_to = assigned_to
                await self.db.flush()
                await self.db.refresh(job)
                return JobRead.model_validate(job)

        job = Job(
            title=title,
            number_of_positions=number_of_positions,
            status_id=status_id,
            positions_filled=positions_filled or 0,
            mandatory_skills=mandatory_skills,
            desired_skills=desired_skills,
            qualification=qualification,
            location=location,
            experience_level=experience_level,
            job_description=job_description,
            department=department,
            is_active=is_active,
            created_by=created_by,
            expires_at=expires_at,
            assigned_to=assigned_to,
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return JobRead.model_validate(job)

    async def get_jobs(self, job_id: int = 0):
        now = datetime.now(timezone.utc)
        if job_id == 0:
            is_expired = case(
                (Job.expires_at.isnot(None) & (Job.expires_at < now), True),
                else_=False,
            ).label("is_expired")

            AssignedUser = User.__table__.alias("assigned_user")

            stmt = (
                select(
                    Job.id, Job.title, Job.department, Job.location,
                    Job.number_of_positions.label("positions"),
                    func.count(JobCandidate.id).label("candidates"),
                    MasterDropdown.value_text.label("status"),
                    is_expired,
                    AssignedUser.c.full_name.label("assigned_to_name"),
                )
                .outerjoin(JobCandidate, (JobCandidate.job_id == Job.id) & (JobCandidate.is_active == True))
                .outerjoin(MasterDropdown, Job.status_id == MasterDropdown.id)
                .outerjoin(AssignedUser, Job.assigned_to == AssignedUser.c.id)
                .where(Job.is_active == True)
                .group_by(Job.id, Job.title, Job.department, Job.location, Job.number_of_positions, MasterDropdown.value_text, Job.expires_at, Job.created, AssignedUser.c.full_name)
                .order_by(Job.created.desc())
            )
            result = await self.db.execute(stmt)
            return [JobListRead(**dict(r._mapping)) for r in result.all()]
        else:
            result = await self.db.execute(select(Job).where(Job.id == job_id))
            rows = result.scalars().all()
            return list(rows)
