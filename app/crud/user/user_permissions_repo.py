from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from app.models.user.user_role_permissions_model import UserRolePermission
from app.models.user.user_roles_model import UserRole
from app.models.user.users_model import User
from app.models.menu_master_model import MenuMaster


class UserPermissionsRepository:
    @staticmethod
    async def get_user_permissions_by_user_name(db: AsyncSession, user_name: str) -> List[Dict[str, Any]]:
        stmt = (
            select(
                UserRolePermission.id,
                UserRolePermission.role_id,
                UserRole.role_name,
                UserRolePermission.menu_id,
                MenuMaster.menu_name,
                UserRolePermission.is_editable,
                UserRolePermission.is_view,
                User.employee_code,
                User.full_name,
                User.user_role_id,
            )
            .join(UserRole, UserRolePermission.role_id == UserRole.id)
            .join(MenuMaster, UserRolePermission.menu_id == MenuMaster.id)
            .join(User, User.user_role_id == UserRole.id)
            .where(User.username == user_name, User.is_active == True)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": r.id, "role_id": r.role_id, "role_name": r.role_name,
                "menu_id": r.menu_id, "menu_name": r.menu_name,
                "is_editable": r.is_editable, "is_view": r.is_view,
                "employee_code": r.employee_code, "full_name": r.full_name,
                "user_role_id": r.user_role_id,
                "route": None, "svg": None,
            }
            for r in rows
        ]
