# app/models/dropdown_model.py
from sqlalchemy import String, BigInteger, ForeignKey, Integer, Boolean, Unicode
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import settings

class MasterDropdownCategory(Base):
    __tablename__ = settings.DROPDOWN_CATEGORY_TABLE_NAME
    __table_args__ = {"extend_existing": True}
    
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        nullable=False
    )
    value_text: Mapped[str] = mapped_column(Unicode(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class MasterDropdown(Base):
    __tablename__ = settings.DROPDOWN_TABLE_NAME
    __table_args__ = {"extend_existing": True}
    
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        nullable=False
    )
    dropdown_category_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey(f"{settings.DROPDOWN_CATEGORY_TABLE_NAME}.id"),
        nullable=False
    )
    value_text: Mapped[str] = mapped_column(Unicode(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
