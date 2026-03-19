from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dropdown.dropdown_model import MasterDropdown, MasterDropdownCategory


class DropdownRepository:
    @staticmethod
    async def get_dropdown_options(db: AsyncSession, category: str) -> list[MasterDropdown]:
        result = await db.execute(
            select(MasterDropdown)
            .join(MasterDropdownCategory, MasterDropdown.dropdown_category_id == MasterDropdownCategory.id)
            .where(MasterDropdownCategory.value_text == category, MasterDropdown.is_active == True)
            .order_by(MasterDropdown.sort_order)
        )
        return list(result.scalars().all())
