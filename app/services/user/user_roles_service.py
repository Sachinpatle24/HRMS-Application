from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.crud.user.user_roles_repo import UserRolesRepository
from app.schemas.user.user_roles_schema import UserRoleSave
from sqlalchemy.exc import DBAPIError

class UserRolesService:
    @staticmethod
    async def get_user_roles(
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        return await UserRolesRepository.get_user_roles(db)

    
    @staticmethod
    async def edit_user_role(
        db: AsyncSession,
        payload: UserRoleSave
    ) -> Dict[str, Any]:
        try:
            return await UserRolesRepository.edit_user_role(db, payload.model_dump())
        
        except DBAPIError as e:
            if "User role with the same name already exists" in str(e.orig):
                raise ValueError("User role with the same name already exists")
            if "User role not found for update" in str(e.orig):
                raise ValueError("User role not found")
            raise

