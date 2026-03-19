# app/crud/candidate_raw_data_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.candidate_rawdata_model import CandidateRawData

class CandidateRawDataRepository:
    @staticmethod
    async def create(db: AsyncSession, entity: CandidateRawData) -> CandidateRawData:
        db.add(entity)
        return entity

    @staticmethod
    async def get_by_candidate_id(db: AsyncSession, candidate_id: int) -> Optional[CandidateRawData]:
        result = await db.execute(
            select(CandidateRawData).where(CandidateRawData.candidate_id == candidate_id)
        )
        return result.scalar_one_or_none()
