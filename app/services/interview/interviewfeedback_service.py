from app.crud.interview.interviewfeedback_repo import FeedbackRepository
from app.schemas.interview.interviewfeedback_schema import (
    InterviewFeedbackUpsert,
    InterviewFeedbackPageResponse,
    CandidateDetail,
    JobDetail,
)
from sqlalchemy.exc import DBAPIError
from datetime import datetime, timezone

class FeedbackService:
    def __init__(self, repo: FeedbackRepository):
        self.repo = repo

    async def upsert_interview_feedback(
        self,
        interview_id: int, 
        payload: InterviewFeedbackUpsert,
        feedback_filename: str | None,
    ):
        if not interview_id:
            raise ValueError("interview_id is required for feedback")
        
        try:
            return await self.repo.upsert_interview_feedback(
                interview_id=interview_id,
                comments=payload.comments,
                upload_feedback_template=payload.upload_feedback_template,
                feedback_filename=feedback_filename,
                rating_id=payload.rating_id,
                result_id=payload.result_id,
                rejection_id=payload.rejection_id,
                feedback_at=datetime.now(timezone.utc),
                active=payload.active,
                status=payload.status,
            )
        except DBAPIError as e:
            if "Interview not found" in str(e.orig):
                raise ValueError("Interview not found")
            raise

    async def download_feedback_file(
        self,
        interview_id: int
    ) -> tuple[bytes, str]:
        row = await self.repo.get_feedback_file(interview_id)

        if not row:
            raise ValueError("Feedback file not found")

        return row["file_bytes"], row["file_name"]
    
    async def get_feedback_page_response(
        self,
        interview_id: int
    ) -> InterviewFeedbackPageResponse:

        row = await self.repo.get_feedback_page_by_interview(interview_id)
        if not row:
            raise ValueError("Interview feedback not found")

        return InterviewFeedbackPageResponse(
            id=row["interview_id"],

            candidate=CandidateDetail(
                id=row["candidate_id"],
                name=row["candidate_name"],
                email=row["email"],
                phone=row["phone"],
                current_company=row["current_company"],
                designation=row["designation"],
                total_experience=row["total_experience"],
                address=row["address"],
                notice_period=row["notice_period"],
                last_working_day=row["last_working_day"],
                skills=row["skills"],
            ),

            job=JobDetail(
                id=row["job_id"],
                position_title=row["position_title"],
                mandatory_skills=row["mandatory_skills"],
                desired_skills=row["desired_skills"],
                qualification=row["qualification"],
            ),

            scheduled_interview_date=row["scheduled_interview_date"],
            scheduled_start_time=row["scheduled_start_time"],

            interviewer_id=row["interviewer_id"],
            is_interviewer_external=row["is_interviewer_external"],
            interviewer_name=row["interviewer_name"],
            interviewer_email_id=row["interviewer_email_id"],

            comments=row["comments"],
            feedback_filename=row["feedback_filename"],
            has_feedback_file=bool(row["has_feedback_file"]),
            feedback_at=row["feedback_at"],

            rating=row["rating_id"],
            result=row["result_id"],
            rejection=row["rejection_id"],

            template_id=row["template_id"],
            template_file_name=row["template_file_name"],
            
            # rating=DropdownRead(
            #     id=row["rating_id"],
            #     value_text=row["rating_value_text"],
            # ) if row["rating_id"] else None,

            # result=DropdownRead(
            #     id=row["result_id"],
            #     value_text=row["result_value_text"],
            # ) if row["result_id"] else None,
        )
