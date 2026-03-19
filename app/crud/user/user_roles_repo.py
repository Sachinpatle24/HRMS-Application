from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from app.models.user.user_roles_model import UserRole


class UserRolesRepository:
    @staticmethod
    async def get_user_roles(db: AsyncSession) -> List[Dict[str, Any]]:
        result = await db.execute(select(UserRole))
        rows = result.scalars().all()
        return [
            {"user_role_id": r.id, "role_name": r.role_name, "description": r.description, "is_active": r.is_active}
            for r in rows
        ]

    @staticmethod
    async def edit_user_role(db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        role = await db.get(UserRole, payload["user_role_id"])
        if not role:
            raise RuntimeError("CreateUserRole did not return a result")
        role.role_name = payload["role_name"]
        role.description = payload.get("description")
        role.is_active = payload.get("is_active", True)
        await db.flush()
        return {"user_role_id": role.id, "role_name": role.role_name, "description": role.description, "is_active": role.is_active}
