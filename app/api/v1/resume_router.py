# app/api/v1/resume_router.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response

from app.schemas.resume_schema import ResumeCreate, ResumeRead, ResumeUpdate, CandidateSearchWithStatusResponse
from app.services.resume_service import ResumeService
from app.services.attachment_service import AttachmentService
from app.core.database import get_db
from app.core.logger import get_custom_logger


router = APIRouter()
logger = get_custom_logger(app_name="resume_router")


@router.get("/", response_model=CandidateSearchWithStatusResponse)
async def list_resumes(
    job_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    complete_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    return await ResumeService.list_resumes(db, job_id, skip, limit, complete_only)


@router.get("/search-candidates", response_model=CandidateSearchWithStatusResponse)
async def search_candidates(
    q: str,
    job_id: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = 50,
    db: AsyncSession = Depends(get_db)
):
    return await ResumeService.search_candidates(db, q, job_id, skip, limit)


@router.get("/download/{id}")
async def download_resume(id: int, db: AsyncSession = Depends(get_db)):
    resume = await ResumeService.get_resume(db, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    attachment = await AttachmentService.get_attachment_for_resume(db, id)
    if not attachment or not attachment.file_data:
        raise HTTPException(status_code=404, detail="Resume file not available")

    media_type = (
        "application/pdf"
        if attachment.file_type == "pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return Response(
        content=attachment.file_data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={attachment.file_name}"}
    )


@router.get("/{id}", response_model=ResumeRead)
async def get_resume(id: int, db: AsyncSession = Depends(get_db)):
    resume = await ResumeService.get_resume(db, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.post("/", response_model=ResumeRead)
async def create_resume(payload: ResumeCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await ResumeService.create_resume(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.patch("/{id}", response_model=ResumeRead)
async def update_resume(id: int, payload: ResumeUpdate, db: AsyncSession = Depends(get_db)):
    resume = await ResumeService.update_resume(db, id, payload)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{id}")
async def delete_resume(id: int, db: AsyncSession = Depends(get_db)):
    success = await ResumeService.delete_resume(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"status": "deleted"}
