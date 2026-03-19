from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResumeUploadResponse(BaseModel):
    status: str
    message: Optional[str] = None
    id: int
    name: Optional[str] = None
    created_at: datetime
    is_duplicate: bool