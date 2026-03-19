from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from datetime import timezone as tz
import re
from fastapi import status

from app.crud.interview.interview_repo import InterviewRepository
from app.schemas.interview.interview_schema import CandidateForJob, ScheduleInterviewRequest, InterviewResponse, ScheduledInterviews, BulkInterviewResponse, BulkInterviewResult
from app.services.interview.email_service import send_email_async
from app.schemas.interview.email_schema import EmailRequest
from app.core.logger import get_custom_logger

from app.core.config import settings

logger = get_custom_logger(app_name="interview_service")


class InterviewService:

    @staticmethod
    def parse_scheduling_error(error: Exception) -> str:
        error_str = str(error)
        if "CANDIDATE_CONFLICT" in error_str:
            return "Candidate already has another interview scheduled in the same time slot."
        elif "INTERVIEWER_CONFLICT" in error_str:
            return "Interviewer already has another interview scheduled in the same time slot."
        elif "STAGE_CONFLICT" in error_str:
            return "An interview is already scheduled or being processed for this Job Candidate."
        else:
            return error_str

    
    @staticmethod
    async def get_candidates_by_job(
        db: AsyncSession, 
        job_id: int
    ) -> List[CandidateForJob]:
        logger.info(f"Fetching candidates for Job: {job_id}")
        
        exists_row = await InterviewRepository.check_job_id(db, job_id)
        if not exists_row:
            raise ValueError(f"Job not found: {job_id}")
        
        rows = await InterviewRepository.get_candidates_by_job_id(db, job_id)
        if not rows:
            raise ValueError(f"No Candidates found for Job: {job_id}")

        candidates = [
            CandidateForJob(**row)
            for row in rows
            if row["candidate_id"] is not None
        ]

        return candidates
    
    
    @staticmethod
    async def get_candidate_interview_history(
        db: AsyncSession,
        candidate_id: int,
        job_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        logger.info(f"Fetching interview history for candidate_id={candidate_id}, job_id={job_id}")

        return await InterviewRepository.get_candidate_interview_history(db, candidate_id, job_id)


    @staticmethod
    async def get_interview_details(
        db: AsyncSession, 
        interview_id: int | None = None
    ) -> List[ScheduledInterviews]:
        row = await InterviewRepository.get_interview_details(db, interview_id)
        if not row:
            return []
        return [ScheduledInterviews(**r) for r in row]
    

    @staticmethod
    async def get_interviews_by_candidate_id(
        db: AsyncSession,
        candidate_id: int
    ) -> list[ScheduledInterviews]:
        """Get all interviews for a candidate. Returns empty list if none found."""
        rows = await InterviewRepository.get_interview_details_by_candidate_id(db, candidate_id)
        return [ScheduledInterviews(**row) for row in rows]
    

    @staticmethod
    async def schedule_interview(
        db: AsyncSession, 
        request: ScheduleInterviewRequest
    ) -> InterviewResponse:
        
        logger.info(f"Scheduling interview for job_candidate_id: {request.job_candidate_id}")
        
        # For edit operations, tamplate_id is optional
        if request.interview_id:
            # Edit operation - tamplate_id optional
            from app.models.interview.interview_model import Interview as InterviewModel
            exists = await db.execute(
                select(InterviewModel.id).where(InterviewModel.id == request.interview_id, InterviewModel.active == True)
            )
            if not exists.scalar():
                raise ValueError("Interview not found or inactive")
        else:
            pass  # Create/reschedule operation
    
        if request.is_interviewer_external:
            if not request.interviewer_name or not request.interviewer_email_id:
                raise ValueError("External interviewer requires name and email")

        # Validate interview mode specific fields
        from app.models.dropdown.dropdown_model import MasterDropdown
        mode_row = None
        if request.interview_mode_id:
            mode_result = await db.execute(
                select(MasterDropdown.value_text).where(MasterDropdown.id == request.interview_mode_id, MasterDropdown.is_active == True)
            )
            mode_row = mode_result.first()
            if mode_row:
                mode_value = mode_row.value_text.strip()
                if mode_value == "Video Call" and not request.video_call_link:
                    raise ValueError("Video call link is required for Video Call mode")
                elif mode_value == "In-Person" and not request.location:
                    raise ValueError("Location is required for In-Person mode")

        duration_row = await db.execute(
            select(MasterDropdown.value_text).where(MasterDropdown.id == request.duration_id, MasterDropdown.is_active == True)
        )

        row = duration_row.fetchone()
        if not row:
            raise ValueError(f"Invalid duration_id: {request.duration_id}")
        
        value = row.value_text.strip().lower()
        match = re.fullmatch(r"(\d+)\s+minutes", value)
        if not match:
            raise ValueError(f"Invalid duration format: {value}")

        duration_minutes = int(match.group(1))

        scheduled_at = datetime.combine(
            request.scheduled_interview_date,
            request.scheduled_start_time
        )

        scheduled_end_time = (scheduled_at + timedelta(minutes=duration_minutes)).time()
        
        # Prevent scheduling in the past  
        if request.active:
            local_tz = tz(timedelta(hours=5, minutes=30))
            scheduled_at_local = scheduled_at.replace(tzinfo=local_tz)
            if scheduled_at_local <= datetime.now(local_tz):
                raise ValueError("Interview cannot be scheduled in the past")      
        
        from app.models.job.job_candidates_model import JobCandidate
        from app.models.resume_model import Resume
        result = await db.execute(
            select(JobCandidate.job_id, JobCandidate.candidate_id, Resume.name, Resume.email)
            .join(Resume, JobCandidate.candidate_id == Resume.id)
            .where(JobCandidate.id == request.job_candidate_id)
        )
        row = result.first()
        
        if not row:
            raise ValueError("Candidate not found")
        
        candidate_id = row.candidate_id
        candidate_name = row.name
        candidate_email = row.email

        if not candidate_email:
            raise ValueError("Candidate email is required for interview scheduling")
        
        interview_id = await InterviewRepository.schedule_interview(
            db=db,
            interview_id=request.interview_id,
            job_id=row.job_id,
            job_candidate_id=request.job_candidate_id,
            candidate_id=candidate_id,
            stage_id=request.stage_id,
            scheduled_interview_date=request.scheduled_interview_date,
            scheduled_start_time=request.scheduled_start_time,
            duration_id=request.duration_id,
            scheduled_end_time=scheduled_end_time,
            is_interviewer_external=request.is_interviewer_external,
            interviewer_id=request.interviewer_id,
            interviewer_name=request.interviewer_name,
            interviewer_email_id=request.interviewer_email_id,
            interview_mode_id=request.interview_mode_id,
            location=request.location,
            video_call_link=request.video_call_link,
            additional_notes=request.additional_notes,
            status=request.status,
            created_by=request.created_by,
            active=request.active,
            template_id=request.tamplate_id 
        )
        
        if not interview_id:
            raise ValueError("Failed to schedule interview")
        
        logger.info(f"Interview scheduled successfully with ID: {interview_id}")

        message = (
            "Interview cancelled successfully"
            if not request.active
            else "Interview updated successfully"
            if request.interview_id
            else "Interview scheduled successfully"
        )
        
        return InterviewResponse(
            success=True,
            status_code = status.HTTP_200_OK,
            interview_id=interview_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            mode_value=mode_row.value_text if mode_row else None,
            is_update=bool(request.interview_id),
            message=message,
            scheduled_at=scheduled_at,
            scheduled_end_time=scheduled_end_time
        )
    

    @staticmethod
    async def send_interview_emails(
        db: AsyncSession,
        interview_data: InterviewResponse,
        request: ScheduleInterviewRequest
    ) -> None:
        """Send emails AFTER DB commit - failures won't rollback"""
        
        # Skip emails for cancelled interviews
        if not request.active:
            logger.info(f"Skipping emails for cancelled interview_id={interview_data.interview_id}")
            return
    
        email_action = "Rescheduled" if interview_data.is_update else "Scheduled"
        feedback_url = settings.FEEDBACK_LINK.format(interview_id=interview_data.interview_id, template_id=request.tamplate_id)
        mode = interview_data.mode_value or ""
        mode_details = ""
        if mode == "Video Call":
            mode_details = f'<li><strong>Video Call Link:</strong> <a href="{request.video_call_link}">{request.video_call_link}</a></li>'
        elif mode == "In-Person":
            mode_details = f'<li><strong>Location:</strong> {request.location}</li>'

        variables = {
            "action": email_action,
            "candidate_name": interview_data.candidate_name,
            "interviewer_name": request.interviewer_name,
            "date": request.scheduled_interview_date.strftime('%Y-%m-%d'),
            "start_time": request.scheduled_start_time.strftime('%H:%M'),
            "end_time": interview_data.scheduled_end_time.strftime('%H:%M') if interview_data.scheduled_end_time else 'N/A',
            "mode_details": mode_details,
            "feedback_url": feedback_url,
            "additional_notes": request.additional_notes or "",
        }

        candidate_subject = f"Interview {email_action} - {interview_data.candidate_name}: {request.scheduled_interview_date.strftime('%Y-%m-%d')}"
        candidate_body = f"""
        <h2>Interview {email_action}</h2>
        <p>Dear {interview_data.candidate_name},</p>
        <p>Your interview has been {email_action.lower()} with the following details:</p>
        <ul>
            <li><strong>Date:</strong> {variables['date']}</li>
            <li><strong>Time:</strong> {variables['start_time']} - {variables['end_time']}</li>
            <li><strong>Interviewer:</strong> {request.interviewer_name}</li>
            {mode_details}
        </ul>
        <p>Good luck!</p>
        """
        interviewer_subject = candidate_subject
        interviewer_body = f"""
        <h2>Interview {email_action}</h2>
        <p>Dear {request.interviewer_name},</p>
        <p>An interview has been {email_action.lower()} with the following details:</p>
        <ul>
            <li><strong>Candidate:</strong> {interview_data.candidate_name}</li>
            <li><strong>Date:</strong> {variables['date']}</li>
            <li><strong>Time:</strong> {variables['start_time']} - {variables['end_time']}</li>
            {mode_details}
            <li><strong>Feedback Link:</strong> <a href="{feedback_url}">{feedback_url}</a></li>
        </ul>
        """

        try: 
            if interview_data.candidate_email and request.interviewer_email_id:
                await send_email_async(EmailRequest(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=[interview_data.candidate_email],
                    cc_emails=[], bcc_emails=[],
                    subject=candidate_subject,
                    body=candidate_body
                ))
                await send_email_async(EmailRequest(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=[request.interviewer_email_id],
                    cc_emails=[], bcc_emails=[],
                    subject=interviewer_subject,
                    body=interviewer_body
                ))
                logger.info(f"Interview emails sent for interview_id={interview_data.interview_id}")
        except Exception as e:
            logger.error(f"Failed to send interview emails: {e}")
    

    @staticmethod
    async def schedule_interviews_bulk(
        db: AsyncSession, 
        request: List[ScheduleInterviewRequest]
    ) -> BulkInterviewResponse:
        """
        Schedule multiple interviews with partial success handling.
        Each interview is processed in its own transaction.
        """
        logger.info(f"Starting bulk interview scheduling for {len(request)} interviews")
        
        results = []
        scheduled_count = 0
        failed_count = 0
        
        for interview_request in request:
            try:
                # Each interview gets its own transaction
                async with db.begin():
                    response = await InterviewService.schedule_interview(db, interview_request)
                
                # Success case
                results.append(BulkInterviewResult(
                    success=True,
                    job_candidate_id=interview_request.job_candidate_id,
                    interview_id=response.interview_id,
                    candidate_id=response.candidate_id,
                    candidate_name=response.candidate_name,
                    candidate_email=response.candidate_email,
                    message=response.message,
                    scheduled_at=response.scheduled_at,
                    scheduled_end_time=response.scheduled_end_time
                ))
                scheduled_count += 1
                
                # Send emails after successful DB commit
                try:
                    await InterviewService.send_interview_emails(db, response, interview_request)
                except Exception as email_error:
                    logger.error(f"Failed to send emails for interview_id {response.interview_id}: {email_error}")
                    
            except Exception as e:
                clean_message = InterviewService.parse_scheduling_error(e)
            
                # Failure case
                logger.error(f"Failed to schedule interview for job_candidate_id {interview_request.job_candidate_id}: {clean_message}")
                results.append(BulkInterviewResult(
                    success=False,
                    job_candidate_id=interview_request.job_candidate_id,
                    interview_id=None,
                    candidate_id=interview_request.candidate_id,
                    candidate_name=None,
                    candidate_email=None,
                    message=clean_message,
                    scheduled_at=None,
                    scheduled_end_time=None
                ))
                failed_count += 1
        
        overall_success = scheduled_count > 0
        
        logger.info(f"Bulk scheduling completed: {scheduled_count} scheduled, {failed_count} failed")
        
        return BulkInterviewResponse(
            status_code=status.HTTP_200_OK if overall_success else status.HTTP_400_BAD_REQUEST,
            success=overall_success,
            total=len(request),
            scheduled=scheduled_count,
            failed=failed_count,
            results=results
        )
    


    

