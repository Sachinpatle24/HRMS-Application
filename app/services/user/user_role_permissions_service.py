from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user.user_role_permissions_repo import UserRolePermissionsRepository
from app.schemas.user.user_role_permissions_schema import UserRoleWithPermissionsSave


class UserRolePermissionsService:
    @staticmethod
    async def get_role_with_permissions(
        db: AsyncSession,
        role_name: str
    ) -> dict:

        rows = await UserRolePermissionsRepository.get_permissions(db, role_name)

        if not rows:
            raise ValueError("Role not found")

        role_info = {
            "role_name": rows[0]["role_name"],
            "description": rows[0]["description"],
            "is_active": rows[0]["is_active"],
            "permissions": []
        }

        for row in rows:
            role_info["permissions"].append({
                "menu_id": row["menu_id"],
                "menu_name": row["menu_name"],
                "is_view": row["is_view"],
                "is_editable": row["is_editable"]
            })

        return role_info

    @staticmethod
    async def upsert_permissions(
        db: AsyncSession,
        payload: UserRoleWithPermissionsSave
    ):
        rows = await UserRolePermissionsRepository.upsert_role_with_permissions(db, payload.model_dump())
    
        role_info = {
            "role_name": rows[0]["role_name"],
            "description": rows[0]["description"],
            "is_active": rows[0]["is_active"],
            "permissions": [],
        }

        for row in rows:
            role_info["permissions"].append({
                "menu_id": row["menu_id"],
                "menu_name": row["menu_name"],
                "is_view": row["is_view"],
                "is_editable": row["is_editable"],
            })

        return role_info
