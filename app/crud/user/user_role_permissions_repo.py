from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Dict, Any
from app.models.user.user_role_permissions_model import UserRolePermission
from app.models.user.user_roles_model import UserRole
from app.models.menu_master_model import MenuMaster


class UserRolePermissionsRepository:
    @staticmethod
    async def upsert_role_with_permissions(db: AsyncSession, payload: Dict[str, Any]):
        result = await db.execute(select(UserRole).where(UserRole.role_name == payload["role_name"]))
        role = result.scalar_one_or_none()

        if role:
            role.description = payload.get("description")
            role.is_active = payload.get("is_active", True)
            await db.execute(delete(UserRolePermission).where(UserRolePermission.role_id == role.id))
        else:
            role = UserRole(
                role_name=payload["role_name"],
                description=payload.get("description"),
                is_active=payload.get("is_active", True),
            )
            db.add(role)
            await db.flush()

        for perm in payload["permissions"]:
            p = perm if isinstance(perm, dict) else perm.model_dump() if hasattr(perm, "model_dump") else dict(perm)
            db.add(UserRolePermission(
                role_id=role.id,
                menu_id=p["menu_id"],
                is_editable=p["is_editable"],
                is_view=p["is_view"],
            ))
        await db.flush()

        return await UserRolePermissionsRepository.get_permissions(db, payload["role_name"])

    @staticmethod
    async def get_permissions(db: AsyncSession, role_name: str):
        stmt = (
            select(
                UserRole.id.label("role_id"), UserRole.role_name, UserRole.description, UserRole.is_active,
                UserRolePermission.menu_id, MenuMaster.menu_name,
                UserRolePermission.is_editable, UserRolePermission.is_view,
            )
            .join(UserRolePermission, UserRole.id == UserRolePermission.role_id)
            .join(MenuMaster, UserRolePermission.menu_id == MenuMaster.id)
            .where(UserRole.role_name == role_name)
        )
        result = await db.execute(stmt)
        return [dict(r._mapping) for r in result.all()]
