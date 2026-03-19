from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from app.models.user.users_model import User
from app.models.user.user_roles_model import UserRole


class UsersRepository:
    @staticmethod
    async def get_user_by_user_id(db: AsyncSession, user_id: str | None = None) -> List[Dict[str, Any]] | None:
        stmt = select(User, UserRole.role_name).join(UserRole, User.user_role_id == UserRole.id)
        if user_id is not None:
            stmt = stmt.where(User.id == int(user_id))
        result = await db.execute(stmt)
        rows = result.all()
        if not rows:
            return None
        return [
            {
                "user_id": u.id, "employee_code": u.employee_code, "username": u.username,
                "email": u.email, "full_name": u.full_name, "user_role_id": u.user_role_id,
                "role_name": role_name, "is_active": u.is_active,
                "created_at": u.created_at, "updated_at": u.updated_at,
            }
            for u, role_name in rows
        ]

    @staticmethod
    async def upsert_user(db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await db.execute(select(User).where(User.username == payload["username"]))
        user = result.scalar_one_or_none()

        if user:
            user.employee_code = payload["employee_code"]
            user.email = payload["email"]
            user.full_name = payload["full_name"]
            user.user_role_id = payload["user_role_id"]
            user.is_active = payload.get("is_active", True)
        else:
            user = User(
                employee_code=payload["employee_code"],
                username=payload["username"],
                email=payload["email"],
                full_name=payload["full_name"],
                user_role_id=payload["user_role_id"],
                is_active=payload.get("is_active", True),
            )
            db.add(user)

        await db.flush()
        await db.refresh(user)
        return {
            "user_id": user.id, "employee_code": user.employee_code, "username": user.username,
            "email": user.email, "full_name": user.full_name, "user_role_id": user.user_role_id,
            "is_active": user.is_active, "created_at": user.created_at, "updated_at": user.updated_at,
        }
