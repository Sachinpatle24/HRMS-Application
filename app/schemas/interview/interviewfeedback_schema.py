from typing import Optional
from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict, model_validator, field_validator
from app.schemas.dropdown.dropdown_schema import DropdownRead

# ---------------------------------------------------------
# Shared Base Schema (fields common to all variants)
# ---------------------------------------------------------
class InterviewBase(BaseModel):    
    scheduled_interview_date: Optional[date] = None
    scheduled_start_time: Optional[time] = None
    scheduled_end_time: Optional[time] = None
    
    duration_id: Optional[int] = None
    stage_id: Optional[int] = None

    is_interviewer_external: Optional[bool] = None 

    interviewer_id: Optional[int] = None
    interviewer_name: Optional[str] = None
    interviewer_email_id: Optional[str] = None
    interview_mode_id: Optional[int] = None

    additional_notes: Optional[str] = None
    comments: Optional[str] = None
    upload_feedback_template: Optional[bytes] = None  # raw binary

    rating_id: Optional[int] = None
    result_id: Optional[int] = None

    active: Optional[bool] = True
    status: Optional[str] = None
    created_by: Optional[int] = None


# ---------------------------------------------------------
# Schema used for Upsert (Create or Update)
# Schema used for API responses 
# - (POST /interview/create-feedback)
# --------------------------------------------------------- 
class InterviewFeedbackUpsert(BaseModel):
    comments: Optional[str] = None
    upload_feedback_template: Optional[bytes] = None
    rating_id: Optional[int] = None
    result_id: Optional[int] = None
    rejection_id: Optional[int] = None

    feedback_at: Optional[datetime] = None
    active: Optional[bool] = None
    status: Optional[str] = None
    
    @model_validator(mode="after")
    def validate_feedback_payload(self):
        feedback_fields = (
            self.comments,
            self.rating_id,
            self.result_id,
            self.rejection_id,
            self.upload_feedback_template,
        )

        if not any(field is not None for field in feedback_fields):
            raise ValueError("At least one feedback field must be provided")

        return self


# ---------------------------------------------------------
# Schema used for API responses 
# - (GET /interview/{interview_id})
# - (GET /interview/{interview_id}/get-feedback)
# Includes primary key ID from SQL Server
# ---------------------------------------------------------
class CandidateDetail(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    current_company: Optional[str] = None
    designation: Optional[str] = None
    total_experience: Optional[float] = None  # in years
    address: Optional[str] = None
    notice_period: Optional[int] = None
    last_working_day: Optional[datetime] = None
    skills: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class JobDetail(BaseModel):
    id: int
    position_title: Optional[str] = None
    mandatory_skills: Optional[str] = None
    desired_skills: Optional[str] = None
    qualification: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class InterviewFeedbackPageResponse(BaseModel):
    id: int
    candidate: CandidateDetail
    job: JobDetail
    
    scheduled_interview_date: date
    scheduled_start_time: time

    interviewer_id: Optional[str] = None
    is_interviewer_external: bool
    interviewer_name: Optional[str] = None
    interviewer_email_id: Optional[str] = None

    comments: Optional[str] = None
    feedback_filename: Optional[str] = None
    has_feedback_file: bool
    rating: Optional[int] = None
    result: Optional[int] = None
    rejection: Optional[int] = None
    feedback_at: Optional[datetime] = None

    template_id: Optional[int] = None
    template_file_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes = True,
    )
