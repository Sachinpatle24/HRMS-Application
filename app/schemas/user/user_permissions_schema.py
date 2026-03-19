from pydantic import BaseModel
from typing import List, Optional


class UserPermissions(BaseModel):
    menu_name: str
    route: Optional[str] = None
    svg: Optional[str] = None
    is_view: bool
    is_editable: bool


class UserPermissionsResponse(BaseModel):
    user_name: str
    employee_code: str
    full_name: str
    role_id: int
    role_name: str
    permissions: List[UserPermissions]
