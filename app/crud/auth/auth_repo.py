from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.user.users_model import User


class AuthRepository:
    @staticmethod
    async def get_user_id_by_username(db: AsyncSession, username: str) -> Optional[int]:
        result = await db.execute(
            select(User.id).where(User.username == username, User.is_active == True)
        )
        return result.scalar_one_or_none()
