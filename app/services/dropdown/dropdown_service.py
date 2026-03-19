from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.dropdown.dropdown_repo import DropdownRepository


class DropdownService:
    @staticmethod
    async def get_dropdown_options(db: AsyncSession, category: str):
        return await DropdownRepository.get_dropdown_options(db, category)
