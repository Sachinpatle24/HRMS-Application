from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.crud.user.user_permissions_repo import UserPermissionsRepository
from app.schemas.user.user_permissions_schema import UserPermissionsResponse, UserPermissions


class UserPermissionsService:
    @staticmethod
    async def get_user_permissions(
        db: AsyncSession,
        user_name: str
    ) -> UserPermissionsResponse:
        rows = await UserPermissionsRepository.get_user_permissions_by_user_name(db, user_name)
        
        if not rows:
            raise ValueError("User not found")
        
        first_row = rows[0]
        
        permissions = [
            UserPermissions(
                menu_name=row["menu_name"],
                route=row["route"],
                svg=row["svg"],
                is_view=bool(row["is_view"]),
                is_editable=bool(row["is_editable"])
            )
            for row in rows
            if row["menu_name"] is not None
        ]
        
        return UserPermissionsResponse(
            user_name=user_name,
            employee_code=first_row["employee_code"],
            full_name=first_row["full_name"],
            role_id=first_row["user_role_id"],
            role_name=first_row["role_name"],
            permissions=permissions
        )
