from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.crud.user.users_repo import UsersRepository
from app.schemas.user.users_schema import UserSave


class UsersService:

    @staticmethod
    async def get_user_for_edit(
        db: AsyncSession,
        user_id: str | None = None
    ) -> List[Dict[str, Any]]:
        user = await UsersRepository.get_user_by_user_id(db, user_id)
        if not user:
            return []
        return user

    @staticmethod
    async def upsert_user(
        db: AsyncSession,
        payload: UserSave
    ) -> Dict[str, Any]:
        return await UsersRepository.upsert_user(db, payload.model_dump())
