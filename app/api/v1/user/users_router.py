from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import List
from app.services.user.users_service import UsersService
from app.services.user.user_permissions_service import UserPermissionsService
from app.schemas.user.users_schema import UserSave, UserRead
from app.schemas.user.user_permissions_schema import UserPermissionsResponse
from app.auth.security import get_current_user
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.get("/get-user", response_model=List[UserRead])
async def get_user(
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    return await UsersService.get_user_for_edit(db, user_id)


@router.get("/get-user-permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_obj = current_user.get("user", {})
    user_name = user_obj.get("user_name") if user_obj else None

    if user_name:
        user_name = user_name.strip()

    if not user_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user_name missing"
        )

    try:
        return await UserPermissionsService.get_user_permissions(db, user_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/create-user", response_model=UserRead)
async def upsert_user(
    payload: UserSave,
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            return await UsersService.upsert_user(db, payload)
    except IntegrityError as e:
        if "UNIQUE KEY constraint" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Username or employee code already exists"
            )
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save user: {str(e)}"
        )
