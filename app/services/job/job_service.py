from app.crud.job.job_repo import JobRepository
from app.schemas.job.job_schema import JobCreate
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError
from app.services.job.job_candidates_service import JobCandidatesService
 
class JobService:
    def __init__(self, db: AsyncSession):
        self.repo = JobRepository(db)
 
    async def create_job(self, payload: JobCreate):
        try:
            row_dict = await self.repo.upsert_job_sp(
                id=None,
                title=payload.title,
                number_of_positions=payload.number_of_positions,
                status_id=payload.status_id,
                positions_filled=payload.positions_filled,
                mandatory_skills=payload.mandatory_skills,
                desired_skills=payload.desired_skills,
                qualification=payload.qualification,
                location=payload.location,
                experience_level=payload.experience_level,
                job_description=payload.job_description,
                department=payload.department,
                is_active=payload.is_active if payload.is_active is not None else True,
                created_by=payload.created_by,
                expires_at=payload.expires_at,
                assigned_to=payload.assigned_to,
            )
            return row_dict
        except DBAPIError as e:
            if "already exists" in str(e):
                raise HTTPException(status_code=409, detail="A Job with this title already exists")
            raise
 
    async def update_job(self, job_id: int, payload: JobCreate):
        existing = await self.repo.get_jobs(job_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Job not found")
       
        existing_job = existing[0]
        provided_fields = payload.model_dump(exclude_unset=True)
       
        def get_value(field_name):
            if field_name in provided_fields:
                return getattr(payload, field_name)
            return getattr(existing_job, field_name)
       
        return await self.repo.upsert_job_sp(
            id=job_id,
            title=payload.title,
            number_of_positions=get_value('number_of_positions'),
            status_id=get_value('status_id'),
            positions_filled=get_value('positions_filled'),
            mandatory_skills=get_value('mandatory_skills'),
            desired_skills=get_value('desired_skills'),
            qualification=get_value('qualification'),
            location=get_value('location'),
            experience_level=get_value('experience_level'),
            job_description=get_value('job_description'),
            department=get_value('department'),
            is_active=get_value('is_active'),
            created_by=payload.created_by,
            expires_at=get_value('expires_at'),
            assigned_to=get_value('assigned_to'),
        )
 
    async def get_jobs(self, job_id: int = 0):
        result = await self.repo.get_jobs(job_id)
        if job_id != 0 and not result:
            raise HTTPException(status_code=404, detail="Job not found")
    
        candidates_service = JobCandidatesService(self.repo.db)
    
        if isinstance(result, list):
            enriched_results = []
            for job in result:
                job_id_value = job.id
                job_candidates = await candidates_service.get_job_candidates(job_id_value)
            
                if hasattr(job, 'model_dump'):
                    job_dict = job.model_dump()
                    job_dict['candidates_details'] = job_candidates
                    enriched_results.append(type(job)(**job_dict))
                else:
                    from app.schemas.job.job_schema import JobRead
                    job_dict = {c.name: getattr(job, c.name) for c in job.__table__.columns}
                    job_dict['candidates'] = job_candidates
                    enriched_results.append(JobRead(**job_dict))
        
            return enriched_results    
        return result
