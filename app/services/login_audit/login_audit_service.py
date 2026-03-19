from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.login_audit.login_audit_schema import LoginAuditCreate
from app.models.login_audit.login_audit_model import LoginAudit
from app.crud.login_audit.login_audit_repo import LoginAuditRepository


class LoginAuditService:

    @staticmethod
    async def create_audit(
        db: AsyncSession,
        audit_data: LoginAuditCreate
    ) -> LoginAudit | None:
        """
        Business layer: orchestrates audit creation
        """

        repo = LoginAuditRepository(db)

        audit_id = await repo.create_login_audit_sp(audit_data)

        if not audit_id:
            return None

        return await repo.get_login_audit_by_id(audit_id)
