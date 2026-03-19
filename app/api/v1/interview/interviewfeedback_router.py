# app/api/v1/interview/interviewfeedback_router.py
from fastapi import APIRouter, UploadFile, HTTPException, File, Form, Depends
from fastapi import status as status_code
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.interview.interviewfeedback_repo import FeedbackRepository
from app.services.interview.interviewfeedback_service import FeedbackService
from app.schemas.interview.interviewfeedback_schema import InterviewFeedbackUpsert, InterviewFeedbackPageResponse


router = APIRouter()


@router.post("/{interview_id}/create-feedback")
async def create_feedback(
    interview_id: int,

    comments: Optional[str] = Form(None),
    rating_id: Optional[int] = Form(None),
    result_id: Optional[int] = Form(None),
    rejection_id: Optional[int] = Form(None),
    active: Optional[bool] = Form(None),
    status: Optional[str] = Form(None),

    upload_feedback_template: Optional[UploadFile] = File(None),

    db: AsyncSession = Depends(get_db)
):
    try:
        file_bytes: bytes | None = None
        filename: str | None = None

        if upload_feedback_template:
            file_bytes = await upload_feedback_template.read()
            filename = upload_feedback_template.filename

        payload = InterviewFeedbackUpsert(
            comments=comments,
            upload_feedback_template=file_bytes,
            rating_id=rating_id,
            result_id=result_id,
            rejection_id=rejection_id,
            active=active,
            status=status,
        )

        async with db.begin():
            repo = FeedbackRepository(db)
            service = FeedbackService(repo)

            await service.upsert_interview_feedback(interview_id, payload, filename)
            return {
                "message": "Feedback saved successfully",
                "interview_id": interview_id,
                "status_code": status_code.HTTP_200_OK
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upsert feedback: {str(e)}"
        )


@router.get("/{interview_id}/get-feedback", response_model=InterviewFeedbackPageResponse)
async def get_feedback(
    interview_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get interview feedback with related details"""
    try:
        repo = FeedbackRepository(db)
        service = FeedbackService(repo)
        return await service.get_feedback_page_response(interview_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Interview Feedback: {str(e)}")
