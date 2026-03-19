from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ResumeAuditLogRead(BaseModel):
    id: int
    candidate_id: int | None
    file_name: str
    resume_status: bool
    free_text: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes = True,
    )
