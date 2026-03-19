# app/api/v1/parser_router.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.core.logger import get_custom_logger
from app.core.database import get_db

from app.schemas.parser_schema import ResumeUploadResponse
from app.services.login_audit.auth_service import AuthService
from app.services.parser_service import ParserService

router = APIRouter()
logger = get_custom_logger(app_name="parser_router")


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_obj = current_user.get("user", {})
    user_name = user_obj.get("user_name") if user_obj else None
    
    if user_name:
        user_name = user_name.strip()
    
    user_id = await AuthService.get_user_id_by_username(user_name, db)
    
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Only PDF/DOCX/DOC allowed")
    
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    file_type = file.filename.split('.')[-1].lower()
    
    logger.info(f"Processing resume file: {file.filename}")

    try:
        resume, metadata = await ParserService.parse_and_ingest_binary(
            db, file_data, file.filename, file_type,
            created_by = user_id
        )

        is_duplicate = metadata.get("deduplication") in ["skipped_existing", "replaced_existing"]

        response = ResumeUploadResponse(
            status="success",
            message="Resume uploaded successfully",
            id=resume.id,
            name=resume.name,
            created_at=resume.created_at,
            is_duplicate=is_duplicate,
        )

        if is_duplicate:
            response.status = "duplicate"
            response.message = "Resume already exists, duplicate detected"

            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=response.model_dump(mode="json"),
            )

        return response
    
    except HTTPException:
        raise

    except ValueError as e:
        error_msg = str(e).lower()
        if "unsupported file type" in error_msg:
            raise HTTPException(status_code=400, detail=str(e))
        elif "no extractable text" in error_msg or "empty" in error_msg:
            raise HTTPException(status_code=400, detail="Unable to extract text from file. File may be corrupted, scanned, or image-only.")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")
