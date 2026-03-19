from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.dashboard.admin_dashboard_repo import get_dashboard_data


async def fetch_dashboard_data(db: AsyncSession):
    return await get_dashboard_data(db)
