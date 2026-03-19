from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.resume_model import Resume
from app.models.job.job_model import Job
from app.models.job.job_candidates_model import JobCandidate
from app.models.interview.interview_model import Interview
from app.models.user.users_model import User


async def get_dashboard_data(db: AsyncSession):
    total_candidates = await db.scalar(select(func.count()).select_from(Resume).where(Resume.active == True)) or 0
    total_jobs = await db.scalar(select(func.count()).select_from(Job).where(Job.is_active == True)) or 0
    total_interviews = await db.scalar(select(func.count()).select_from(Interview).where(Interview.active == True)) or 0
    total_users = await db.scalar(select(func.count()).select_from(User).where(User.is_active == True)) or 0

    candidate_count_sub = (
        select(JobCandidate.job_id, func.count().label("cnt"))
        .where(JobCandidate.is_active == True)
        .group_by(JobCandidate.job_id)
        .subquery()
    )
    recent_jobs_stmt = (
        select(
            Job.id.label("job_id"),
            Job.title,
            Job.department,
            Job.location,
            Job.number_of_positions.label("positions"),
            func.coalesce(candidate_count_sub.c.cnt, 0).label("candidate_count"),
        )
        .outerjoin(candidate_count_sub, Job.id == candidate_count_sub.c.job_id)
        .where(Job.is_active == True)
        .order_by(Job.id.desc())
        .limit(5)
    )
    result = await db.execute(recent_jobs_stmt)
    recent_jobs = [
        {**dict(r._mapping), "status": "Open"}
        for r in result.all()
    ]

    return {
        "total_candidates": total_candidates,
        "total_jobs": total_jobs,
        "total_interviews": total_interviews,
        "total_users": total_users,
        "recent_jobs": recent_jobs,
    }
