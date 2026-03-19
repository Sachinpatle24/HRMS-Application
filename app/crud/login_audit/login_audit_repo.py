from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.login_audit.login_audit_schema import LoginAuditCreate
from app.models.login_audit.login_audit_model import LoginAudit


class LoginAuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_login_audit_sp(self, audit_data: LoginAuditCreate) -> int | None:
        audit = LoginAudit(
            username=audit_data.username,
            employee_id=audit_data.employee_id,
            token=audit_data.token,
        )
        self.db.add(audit)
        await self.db.flush()
        return audit.id

    async def get_login_audit_by_id(self, audit_id: int) -> LoginAudit | None:
        return await self.db.get(LoginAudit, audit_id)
