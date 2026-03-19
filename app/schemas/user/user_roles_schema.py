from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserRoleSave(BaseModel):
    user_role_id: Optional[int] = None
    role_name: str
    description: Optional[str] = None
    is_active: bool
    
class UserRoleRead(BaseModel):
    user_role_id: int
    role_name: str
    description: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
