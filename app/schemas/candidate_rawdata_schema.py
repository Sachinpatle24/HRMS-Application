# app/schemas/candidate_raw_data_schema.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------
# Shared base schema
# ---------------------------------------------------------
class CandidateRawDataBase(BaseModel):
    candidate_id: int
    raw_text: Optional[str] = None
    parsed_json: Optional[str] = None

# ---------------------------------------------------------
# Schema used during creation (POST /attachments)
# ---------------------------------------------------------
class CandidateRawDataCreate(CandidateRawDataBase):
    pass

# ---------------------------------------------------------
# Schema used for API responses (GET)
# ---------------------------------------------------------
class CandidateRawDataRead(BaseModel):
    id: int
    candidate_id: int
    raw_text: Optional[str] = None
    parsed_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
