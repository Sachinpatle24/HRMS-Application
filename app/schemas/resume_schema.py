from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pydantic import field_validator, field_serializer
import json

def _format_address(address_json: str) -> str:
    if not address_json:
        return ""
    try:
        addresses = json.loads(address_json)
        if not addresses:
            return ""
        addr = addresses[0]
        parts = [addr.get("street"), addr.get("city"), addr.get("state"), 
                 addr.get("zip"), addr.get("country")]
        return ", ".join(str(p).strip() for p in parts if p and str(p).strip())
    except Exception:
        return address_json

# ---------------------------------------------------------
# Shared Base Schema (fields common to all variants)
# ---------------------------------------------------------
class ResumeBase(BaseModel):
    # Personal Details
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_number: Optional[str] = None
    website: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

    # Summary
    summary: Optional[str] = None

    # Education
    education: Optional[str] = None

    # Work Experience (stored as stringified JSON)
    work_experience: Optional[str] = None

    # Skills (string or stringified list)
    skills: Optional[str] = None

    # Certifications
    certifications: Optional[str] = None

    # Projects
    projects: Optional[str] = None

    # File metadata
    file_name: Optional[str] = None

    # Computed fields
    total_experience: Optional[float] = None
    total_experience_pretty: Optional[str] = None

    # Company-wise experience (stringified JSON)
    experience_per_company: Optional[str] = None
    experience_per_company_pretty: Optional[str] = None

    # User-only fields (Category B - not parsed)
    current_company: Optional[str] = None
    designation: Optional[str] = None
    last_working_day: Optional[datetime] = None
    notice_period: Optional[int] = None

    active: Optional[bool] = True
    created_by: Optional[int] = None

# ---------------------------------------------------------
# Schema used during creation (POST /resumes)
# All fields optional because parser fills dynamically.
# ---------------------------------------------------------
class ResumeCreate(ResumeBase):
    pass


# ---------------------------------------------------------
# Schema used for partial updates (PATCH-like behavior)
# Only editable fields are included.
# ---------------------------------------------------------
class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_number: Optional[str] = None
    website: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

    summary: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    projects: Optional[str] = None

    active: Optional[bool] = True
    created_by: Optional[int] = None

    # Updating computed fields manually is typically not allowed
    # but if needed uncomment the following lines:
    # total_experience: Optional[float] = None
    # total_experience_pretty: Optional[str] = None


# ---------------------------------------------------------
# Schema used for confirmational updates (PATCH-like behavior)
# Only frontend visible fields are included.
# ---------------------------------------------------------
class ResumeConfirmationPayload(BaseModel):
    # Parsed-but-correctable fields
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_number: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    total_experience: Optional[float] = None
    
    # User-only fields (not parsed)
    current_company: Optional[str] = None
    designation: Optional[str] = None
    last_working_day: Optional[datetime] = None
    notice_period: Optional[int] = None

    created_by: Optional[int] = None 

    @field_validator("*", mode="before")
    @classmethod
    def reject_placeholder_strings(cls, v):
        if isinstance(v, str) and v.strip().lower() in {"string", ""}:
            return None
        return v


class ResumeConfirmResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    candidate_id: int


# ---------------------------------------------------------
# Schema used for API responses (GET /resumes/{id})
# Includes primary key ID from SQL Server.
# ---------------------------------------------------------
class ResumeRead(ResumeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_complete: bool
    active: bool

    @field_serializer('address')
    def serialize_address(self, address: str) -> str:
        return _format_address(address)
    
    model_config = ConfigDict(
        from_attributes = True,
    )


class CandidateWithStatus(BaseModel):
    id: int
    name: Optional[str]
    total_experience: Optional[float]
    total_experience_pretty: Optional[str]
    skills: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    file_name: Optional[str]
    AddOrRemove: int
    
    @field_serializer('address')
    def serialize_address(self, address: str) -> str:
        return _format_address(address)
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')


class CandidateSearchWithStatusResponse(BaseModel):
    candidates: list[CandidateWithStatus]
    total_candidates: int
    