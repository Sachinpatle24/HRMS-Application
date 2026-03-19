from pydantic import BaseModel
from typing import List, Optional

class RecentJob(BaseModel):
    job_id: int
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    positions: int = 0
    candidate_count: int = 0
    status: str = "Open"

class DashboardResponse(BaseModel):
    total_candidates: int = 0
    total_jobs: int = 0
    total_interviews: int = 0
    total_users: int = 0
    recent_jobs: List[RecentJob] = []
