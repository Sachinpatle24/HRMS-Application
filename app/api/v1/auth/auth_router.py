# app/api/v1/auth_router.py

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.login_audit.auth_service import AuthService
from app.auth.security import get_current_user
from app.core.database import get_db

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    status: int
    message: str
    user: dict 

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            token, user_details = await AuthService.login_user(
                payload.username,
                payload.password,
                db
            )
            
        return TokenResponse(
            access_token=token,
            status=200,
            message="Login successful",
            user=user_details
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": 401, "message": str(e)}
        )

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await AuthService.logout_user(
        current_user.get("username"),
        current_user.get("jti"),
        db
    )
    
    return {"status": 200, "message": "Logout successful"}
