from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.job.job_candidates_service import JobCandidatesService
from app.schemas.job.job_candidates_schema import JobCandidateCreate, JobCandidatesResponse, JobCandidateStatusUpdate, JobCandidateRead
from app.schemas.job.stage_history_schema import StageHistoryRead

router = APIRouter()

@router.post("/add-candidates", status_code=status.HTTP_200_OK)
async def add_candidates_to_job(
    payload: list[JobCandidateCreate],
    db: AsyncSession = Depends(get_db)
):
    """Add multiple candidates to a Job or soft delete by setting is_active=False"""
    try:
        async with db.begin():
            service = JobCandidatesService(db)
            return await service.add_candidates_to_job(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add candidates to Job: {str(e)}"
        )

@router.get("/get-job-candidates/{job_id}", response_model=JobCandidatesResponse)
async def get_job_candidates(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all active candidates for a specific Job"""
    try:
        service = JobCandidatesService(db)
        return await service.get_job_candidates(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Job candidates: {str(e)}"
        )


@router.get("/stage-history/{job_candidate_id}", response_model=list[StageHistoryRead])
async def get_stage_history(
    job_candidate_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = JobCandidatesService(db)
    return await service.get_stage_history(job_candidate_id)


@router.patch("/update-status/{job_candidate_id}", response_model=JobCandidateRead)
async def update_candidate_status(
    job_candidate_id: int,
    payload: JobCandidateStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update candidate workflow status with state machine validation"""
    try:
        async with db.begin():
            service = JobCandidatesService(db)
            return await service.update_status(job_candidate_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
