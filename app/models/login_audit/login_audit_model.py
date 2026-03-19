# app/models/loginaudit_model.py
from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import settings

class LoginAudit(Base):
    __tablename__ = settings.LOGIN_AUDIT_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(String(), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    token: Mapped[str] = mapped_column(String(), nullable=False)
    
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )
