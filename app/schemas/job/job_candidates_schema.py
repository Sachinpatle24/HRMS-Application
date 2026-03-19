from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from typing_extensions import Literal

class JobCandidateCreate(BaseModel):
    job_id: int
    candidate_id: int
    current_stage_id: Optional[int] = None
    current_result_id: Optional[int] = None
    created_by: int
    is_active: bool = True
    status: Optional[str] = "Applied"


class JobCandidateRead(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    current_stage_id: Optional[int]
    current_result_id: Optional[int]
    created: datetime
    updated: datetime
    created_by: int
    is_active: bool
    status: str = "Applied"

    model_config = ConfigDict(from_attributes=True, extra='ignore')

class JobCandidateDetail(BaseModel):
    candidate_id: int
    name: Optional[str]
    total_experience_pretty: Optional[str]
    skills: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    file_name: Optional[str]
    status: str = "Applied"

    model_config = ConfigDict(from_attributes=True, extra='ignore')

class JobCandidatesResponse(BaseModel):
    total_candidates: int
    candidates: list[JobCandidateDetail]

class JobCandidatesBulkCreate(BaseModel):
    candidates: list[JobCandidateCreate]

class JobCandidateStatusUpdate(BaseModel):
    status: str
    created_by: int


class JobCandidateActionResponse(BaseModel):
    action: Literal["created", "deleted"]
    candidate: JobCandidateRead
