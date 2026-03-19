from app.crud.job.job_candidates_repo import JobCandidatesRepository
from app.schemas.job.job_candidates_schema import JobCandidateCreate, JobCandidateRead, JobCandidateStatusUpdate
from app.schemas.job.stage_history_schema import StageHistoryRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import ProgrammingError
from typing import List


class JobCandidatesService:
    def __init__(self, db: AsyncSession):
        self.repo = JobCandidatesRepository(db)

    async def add_candidate_to_job(self, payload: JobCandidateCreate):
        try:
            result = await self.repo.insert_job_candidate_sp(
                job_id=payload.job_id,
                candidate_id=payload.candidate_id,
                current_stage_id=payload.current_stage_id,
                current_result_id=payload.current_result_id,
                created_by=payload.created_by,
                is_active=payload.is_active
            )

            if not result:
                return None

            return {
                "action": "deleted" if payload.is_active is False else "created",
                "candidate": result
            }
        except ProgrammingError as e:
            if "Candidate is already active" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail=f"Candidate {payload.candidate_id} is already active for Job {payload.job_id}"
                )
            raise
    
    async def add_candidates_to_job(self, payloads: list[JobCandidateCreate]):
        responses = []

        for payload in payloads:
            result = await self.add_candidate_to_job(payload)
            if result:
                responses.append(result)

        return {
            "requested_count": len(payloads),
            "processed_count": len(responses),
            "results": responses
        }
    
    async def get_job_candidates(self, job_id: int):
        return await self.repo.get_job_candidates_sp(job_id)

    async def get_stage_history(self, job_candidate_id: int) -> List[StageHistoryRead]:
        return await self.repo.get_stage_history(job_candidate_id)

    async def update_status(self, job_candidate_id: int, payload: JobCandidateStatusUpdate) -> JobCandidateRead:
        return await self.repo.update_status(job_candidate_id, payload.status, payload.created_by)
