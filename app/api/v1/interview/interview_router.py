from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from urllib.parse import unquote

from app.schemas.interview.interview_schema import ScheduleInterviewRequest, InterviewResponse, CandidatesByJobResponse, CandidateInterviewHistory, ScheduledInterviews, BulkInterviewResponse
from app.services.interview.interview_service import InterviewService
from app.core.database import get_db
from app.core.logger import get_custom_logger

router = APIRouter()
logger = get_custom_logger(app_name="interview_router")


@router.get("/get-candidates-by-job/{job_id}", response_model=CandidatesByJobResponse)
async def get_candidates_by_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all candidates for a given Job ID.
    """
    try: 
        logger.info(f"Fetching candidates for Job: {job_id}")
        
        candidates = await InterviewService.get_candidates_by_job(db, job_id)

        return {
            "job_id": job_id,
            "total_candidates": len(candidates),
            "candidates": candidates
        }
    except ValueError as exc:
        raise HTTPException(status_code=200, detail=str(exc))


@router.get("/candidates/{candidate_id}/interview-history", response_model=List[CandidateInterviewHistory])
async def get_candidate_interview_history(
    candidate_id: int,
    job_id: Optional[int] = None,
    candidate_name: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        history = await InterviewService.get_candidate_interview_history(db, candidate_id, job_id)
        return history
    
    except Exception as e:
        logger.error(f"Interview history error: {str(e)}", exc_info=True)
        if "Invalid candidate_id" in str(e):
            name = unquote(candidate_name) if candidate_name else "Candidate"
            raise HTTPException(status_code=200, detail=f"{name}'s interview has not been scheduled yet.")
        raise HTTPException(status_code=200, detail="Failed to fetch interview history")


@router.get("/interview", response_model=List[ScheduledInterviews])
async def get_interview_details(
    interview_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch interview details for a given interview ID.
    If interview_id is NULL, fetch all interviews.
    If interview_id > 0, fetch details for that interview only.
    """
    try:
        return await InterviewService.get_interview_details(db, interview_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch interview details")


@router.get("/{candidate_id}/interviews", response_model=List[ScheduledInterviews])
async def get_candidate_interviews(
    candidate_id: int,
    candidate_name: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all scheduled interviews for a candidate.
    """
    try:
        return await InterviewService.get_interviews_by_candidate_id(db, candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        if "Invalid candidate_id" in str(exc):
            name = unquote(candidate_name) if candidate_name else "Candidate"
            raise HTTPException(status_code=200, detail=f"{name}'s interview has not been scheduled yet.")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate interviews")


@router.post("/schedule-interview", response_model=InterviewResponse)
async def schedule_interview(
    request: ScheduleInterviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a new interview for a candidate.
    """
    logger.info(f"Scheduling interview for candidate: {request.job_candidate_id}")
    
    try:
        async with db.begin():
            response = await InterviewService.schedule_interview(db, request)
        await InterviewService.send_interview_emails(db, response, request)
        return response

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        clean_message = InterviewService.parse_scheduling_error(exc)
        
        if "Candidate already has another interview scheduled" in clean_message:
            raise HTTPException(status_code=409, detail={"type": "Interview Conflict", "message": clean_message})
        if "Interviewer already has another interview scheduled" in clean_message:
            raise HTTPException(status_code=409, detail={"type": "Interview Conflict", "message": clean_message})
        if "already scheduled or being processed" in clean_message.lower():
            raise HTTPException(status_code=409, detail={"type": "Scheduling Conflict", "message": clean_message})
        
        logger.error(f"Failed to schedule interview: {clean_message}")
        raise HTTPException(status_code=500, detail="Failed to schedule interview")


@router.post("/schedule-interviews-bulk", response_model=BulkInterviewResponse)
async def schedule_interviews_bulk(
    request: List[ScheduleInterviewRequest],
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule multiple interviews with partial success handling.
    Each interview is processed independently - failures don't affect other interviews.
    """
    logger.info(f"Bulk scheduling {len(request)} interviews")
    
    if not request:
        raise HTTPException(status_code=400, detail="No interviews schedule requests provided")
    
    try:
        return await InterviewService.schedule_interviews_bulk(db, request)
    except Exception as exc:
        logger.error(f"Bulk interview scheduling failed: {str(exc)}")
        raise HTTPException(status_code=500, detail="Bulk interview scheduling failed")
