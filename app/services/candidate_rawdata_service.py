# app/services/candidate_raw_data_service.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.candidate_rawdata_repo import CandidateRawDataRepository
from app.schemas.candidate_rawdata_schema import CandidateRawDataCreate
from app.models.candidate_rawdata_model import CandidateRawData

class CandidateRawDataService:

    @staticmethod
    async def upsert_raw_data(
        db: AsyncSession,
        payload: CandidateRawDataCreate,
        *,
        replace: bool = True
    ) -> CandidateRawData:
        """
        One-to-one raw data semantics:
        - Exactly one raw data row per resume
        - Created eagerly during ingestion
        """

        existing = await CandidateRawDataRepository.get_by_candidate_id(
            db, payload.candidate_id
        )

        if existing:
            if replace:
                existing.raw_text = payload.raw_text
                existing.parsed_json = payload.parsed_json
            return existing

        raw_data = CandidateRawData(**payload.model_dump())
        await CandidateRawDataRepository.create(db, raw_data)
        await db.flush()

        return raw_data
    
    @staticmethod
    async def get_by_candidate_id(
        db: AsyncSession,
        candidate_id: int
    ) -> Optional[CandidateRawData]:
        return await CandidateRawDataRepository.get_by_candidate_id(db, candidate_id)


