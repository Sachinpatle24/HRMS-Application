from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class StageHistoryRead(BaseModel):
    id: int
    job_candidate_id: int
    from_stage: Optional[str] = None
    to_stage: Optional[str] = None
    from_result: Optional[str] = None
    to_result: Optional[str] = None
    changed_by_name: Optional[str] = None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
