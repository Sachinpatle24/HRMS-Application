# app/services/auth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.security import create_access_token
from app.crud.auth.auth_repo import AuthRepository
from app.services.login_audit.login_audit_service import LoginAuditService
from app.schemas.login_audit.login_audit_schema import LoginAuditCreate
from app.core.config import settings
from app.core.logger import get_custom_logger

logger = get_custom_logger("auth_service")

class AuthService:
    
    @staticmethod
    async def get_user_id_by_username(username: str, db: AsyncSession):
        user_id = await AuthRepository.get_user_id_by_username(db, username)
        return user_id
    

    @staticmethod
    async def login_user(username: str, password: str, db: AsyncSession):
        """
        Authenticate user with local hardcoded credentials.
        
        Returns:
            tuple: (access_token, user_details) or raises ValueError
        """
        if username != settings.LOCAL_AUTH_USERNAME or password != settings.LOCAL_AUTH_PASSWORD:
            logger.warning(f"Failed login attempt for user: {username}")
            raise ValueError("Invalid credentials")
        
        user_details = {
            "user_name": username,
            "job_title": None,
            "department": None,
            "work_location": None,
            "employee_id": None,
        }

        user_details["user_id"] = await AuthService.get_user_id_by_username(username, db)

        token = create_access_token({
            "sub": username,
            "auth_method": "local",
            "user": user_details,
        })
        
        audit_data = LoginAuditCreate(
            username=username,
            employee_id=user_details.get("employee_id"),
            token=token
        )
        await LoginAuditService.create_audit(db, audit_data)

        
        logger.info(f"Successful login for user: {username}")
        return token, user_details
    

    @staticmethod
    async def logout_user(username: str, token: str, db: AsyncSession):
        """Log user logout event."""
        logger.info(f"User logged out: {username}")
        return True
