# app/schemas/attachment_schema.py

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------
# Shared base schema
# ---------------------------------------------------------
class AttachmentBase(BaseModel):
    candidate_id: int
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_data: Optional[bytes] = None
    status: Optional[str] = "active"

# ---------------------------------------------------------
# Schema used during creation (POST /attachments)
# ---------------------------------------------------------
class AttachmentCreate(AttachmentBase):
    pass

# ---------------------------------------------------------
# Schema used for API responses (GET)
# ---------------------------------------------------------
class AttachmentRead(BaseModel):
    id: int
    candidate_id: int
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    # Do not expose binary data in responses
    file_data: Optional[bytes] = Field(exclude=True)

    model_config = ConfigDict(
        from_attributes=True
    )
