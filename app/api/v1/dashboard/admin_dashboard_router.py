from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.dashboard.admin_dashboard_schema import DashboardResponse
from app.services.dashboard.admin_dashboard_service import fetch_dashboard_data

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    return await fetch_dashboard_data(db)
