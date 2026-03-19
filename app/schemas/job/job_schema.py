from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.job.job_candidates_schema import JobCandidatesResponse
 
class JobBase(BaseModel):
    id: Optional[int] = None
    title: str
    number_of_positions: Optional[int] = 0
    mandatory_skills: Optional[str] = None
    desired_skills: Optional[str] = None
    qualification: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    job_description: Optional[str] = None
    status_id: Optional[int] = None
    department: Optional[str] = None
    positions_filled: Optional[int] = 0
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    created_by: int
    assigned_to: Optional[int] = None
 
 
class JobCreate(JobBase):
    pass
 
class JobRead(JobBase):
    id: int
    is_active: bool
    created_by: int
    assigned_to: Optional[int] = None
    created: datetime
    updated: datetime
    candidates: Optional[JobCandidatesResponse] = None
 
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )
    
class JobListRead(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    positions: int
    candidates: int
    status: Optional[str] = None
    is_expired: bool = False
    assigned_to_name: Optional[str] = None
 
    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )
