from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user.user_role_permissions_service import UserRolePermissionsService
from app.schemas.user.user_role_permissions_schema import (
    UserRoleWithPermissionsRead,
    UserRoleWithPermissionsSave,
)

router = APIRouter()


@router.get("/{role_name}",response_model=UserRoleWithPermissionsRead)
async def get_user_role_permissions(
    role_name: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await UserRolePermissionsService.get_role_with_permissions(db, role_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upsert",response_model=UserRoleWithPermissionsRead)
async def upsert_user_role_permissions(
    payload: UserRoleWithPermissionsSave,
    db: AsyncSession = Depends(get_db),
):
    try:
        async with db.begin():
            return await UserRolePermissionsService.upsert_permissions(db, payload)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))