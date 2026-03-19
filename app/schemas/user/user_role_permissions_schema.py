from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional


class UserRolePermissionItem(BaseModel):
    menu_id: int
    menu_name: str
    is_view: bool
    is_editable: bool

    # @field_validator('is_editable')
    # @classmethod
    # def validate_is_editable(cls, v, info):
    #     if not info.data.get('is_view', True):
    #         return False
    #     return v


class UserRoleWithPermissionsSave(BaseModel):
    role_name: str
    description: Optional[str] = None
    permissions: List[UserRolePermissionItem]
    is_active: bool = True


class UserRoleWithPermissionsRead(BaseModel):
    role_name: str
    description: Optional[str] = None
    permissions: List[UserRolePermissionItem]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    