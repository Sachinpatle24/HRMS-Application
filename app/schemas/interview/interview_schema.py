from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import ConfigDict


class CandidateForJob(BaseModel):
    job_id: int
    job_candidate_id: int
    candidate_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    total_experience: Optional[float] = None
    skills: Optional[str] = None


class CandidatesByJobResponse(BaseModel):
    job_id: int
    total_candidates: int
    candidates: List[CandidateForJob]

class ScheduleInterview(BaseModel):
    job_id: int 
    job_candidate_id: int
    candidate_id: int
    scheduled_interview_date: date
    scheduled_start_time: time
    stage_id: int
    stage_name: Optional[str] = None
    result_id: Optional[int] = None
    duration_id: int
    interviewer_id: str
    interviewer_name: Optional[str] = None
    interviewer_email_id: Optional[str] = None
    interview_mode_id: int
    location: Optional[str] = None
    video_call_link: Optional[str] = None
    is_interviewer_external: bool = False
    additional_notes: Optional[str] = None
    status: str = 'Scheduled'
    created_by: int

class ScheduleInterviewRequest(ScheduleInterview):
    interview_id: Optional[int] = None
    tamplate_id: Optional[int] = None
    interviewer_name: str
    interviewer_email_id: str
    active: bool = True


class InterviewResponse(BaseModel):
    success: bool
    status_code: int
    interview_id: int
    candidate_id: int
    candidate_name: str
    candidate_email: Optional[str] = None
    mode_value: Optional[str] = None
    is_update: bool
    message: str
    scheduled_at: datetime
    scheduled_end_time: Optional[time] = None
    
class CandidateInterviewHistory(BaseModel):
    interview_id: Optional[int] = None 
    stage_id: int
    stage_name: str
    interviewer_id: Optional[str] = None
    interviewer_name: Optional[str] = None
    scheduled_interview_date: date
    rating_id: Optional[int] = None
    result_id: Optional[int] = None
    status: str
    placeholder:Optional[str] = None
    comments: Optional[str] = None
    has_feedback_file: bool = False
    feedback_filename:Optional[str] = None
    template_filename: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# class ScheduledInterviewView(ScheduleInterview):
#     interview_id: int
#     scheduled_end_time: Optional[time] = None
#     created_at: datetime
#     updated_at: Optional[datetime] = None

class ScheduledInterviews(ScheduleInterview):
    interview_id: int
    job_id: int
    candidate_name: Optional[str] = None
    designation: Optional[str] = None
    scheduled_end_time: Optional[time] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    template_id: Optional[int] = None
    result_name: Optional[str] = None


# Bulk Interview Scheduling
class BulkInterviewResult(BaseModel):
    success: bool
    job_candidate_id: Optional[int]
    interview_id: Optional[int] = None
    candidate_id: Optional[int] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    message: str
    scheduled_at: Optional[datetime] = None
    scheduled_end_time: Optional[time] = None


class BulkInterviewResponse(BaseModel):
    status_code: int
    success: bool
    total: int
    scheduled: int
    failed: int
    results: List[BulkInterviewResult]