# app/schemas/login_audit_schema.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LoginAuditBase(BaseModel):
    username: str
    employee_id: Optional[str] = None
    token: str

class LoginAuditCreate(LoginAuditBase):
    pass

class LoginAuditRead(BaseModel):
    id: int
    username: str
    employee_id: Optional[str] = None
    token: str
    created: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
