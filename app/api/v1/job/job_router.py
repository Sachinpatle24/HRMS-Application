from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.core.database import get_db
from app.services.job.job_service import JobService
from app.schemas.job.job_schema import JobCreate, JobRead, JobListRead
 
from typing import Union
 
router = APIRouter()
 
 
@router.post("/create-job", status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            service = JobService(db)
 
            if payload.id:
                result = await service.update_job(payload.id, payload)
                return {
                    "message": "Job updated successfully",
                    "data": result,
                    "status_code": status.HTTP_200_OK
                }
 
            result = await service.create_job(payload)
            return {
                "message": "Job created successfully",
                "data": result,
                "status_code": status.HTTP_201_CREATED
            }
    except HTTPException as http_exc:
        if http_exc.status_code == 409:
            return {
                "message": http_exc.detail,
                "status_code": status.HTTP_409_CONFLICT
            }
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upsert Job: {str(e)}"
        )
 
 
@router.get("/get-job/{job_id}", response_model=Union[list[JobListRead], list[JobRead]])
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get Job(s) - returns list view when job_id=0, detail view otherwise"""
    try:
        service = JobService(db)
        return await service.get_jobs(job_id)
 
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Job: {str(e)}"
        )
