from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UserSave(BaseModel):
    employee_code: str
    username: str
    email: str
    full_name: str
    user_role_id: int
    is_active: bool
    parent_id: Optional[int] = None


class UserRead(BaseModel):
    user_id: int
    employee_code: str
    username: str
    email: str
    full_name: str
    user_role_id: int
    role_name: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSimple(BaseModel):
    user_id: int
    full_name: str
