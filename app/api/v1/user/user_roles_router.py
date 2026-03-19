from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import List
from app.services.user.user_roles_service import UserRolesService
from app.schemas.user.user_roles_schema import UserRoleRead, UserRoleSave

router = APIRouter()


@router.get("/user-roles", response_model=List[UserRoleRead])
async def list_user_roles(
    db: AsyncSession = Depends(get_db)
):
    return await UserRolesService.get_user_roles(db)

@router.post("/edit-user-roles", response_model=UserRoleRead)
async def edit_user_role(
    payload: UserRoleSave,
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            return await UserRolesService.edit_user_role(db, payload)

    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        elif "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit user role: {str(e)}"
        )
