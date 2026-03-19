from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.dropdown.dropdown_service import DropdownService

router = APIRouter()


@router.get("/{category}")
async def get_dropdown_options(category: str, db: AsyncSession = Depends(get_db)):
    return await DropdownService.get_dropdown_options(db, category)
