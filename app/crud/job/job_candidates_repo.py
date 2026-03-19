from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
from typing import List
from app.models.job.job_candidates_model import JobCandidate
from app.models.job.stage_history_model import StageHistory
from app.models.resume_model import Resume
from app.models.user.users_model import User
from app.models.dropdown.dropdown_model import MasterDropdown
from app.schemas.job.job_candidates_schema import JobCandidateRead, JobCandidateDetail, JobCandidatesResponse
from app.schemas.job.stage_history_schema import StageHistoryRead
from app.services.job.candidate_workflow import validate_transition


class JobCandidatesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert_job_candidate_sp(
        self,
        job_id: int,
        candidate_id: int,
        current_stage_id: int | None,
        current_result_id: int | None,
        created_by: int,
        is_active: bool,
    ):
        result = await self.db.execute(
            select(JobCandidate).where(JobCandidate.job_id == job_id, JobCandidate.candidate_id == candidate_id)
        )
        jc = result.scalar_one_or_none()

        if jc:
            old_stage = jc.current_stage_id
            old_result = jc.current_result_id
            jc.current_stage_id = current_stage_id
            jc.current_result_id = current_result_id
            jc.is_active = is_active
            await self.db.flush()

            # Record stage transition if stage or result changed
            if old_stage != current_stage_id or old_result != current_result_id:
                self.db.add(StageHistory(
                    job_candidate_id=jc.id,
                    from_stage_id=old_stage, to_stage_id=current_stage_id,
                    from_result_id=old_result, to_result_id=current_result_id,
                    changed_by=created_by,
                ))
                await self.db.flush()
        else:
            jc = JobCandidate(
                job_id=job_id, candidate_id=candidate_id,
                current_stage_id=current_stage_id, current_result_id=current_result_id,
                created_by=created_by, is_active=is_active, status="Applied",
            )
            self.db.add(jc)
            await self.db.flush()

            # Record initial stage assignment
            if current_stage_id or current_result_id:
                self.db.add(StageHistory(
                    job_candidate_id=jc.id,
                    from_stage_id=None, to_stage_id=current_stage_id,
                    from_result_id=None, to_result_id=current_result_id,
                    changed_by=created_by,
                ))
                await self.db.flush()

        await self.db.refresh(jc)
        return JobCandidateRead.model_validate(jc)

    async def get_job_candidates_sp(self, job_id: int):
        stmt = (
            select(
                JobCandidate.id, JobCandidate.job_id, JobCandidate.candidate_id,
                Resume.name, Resume.email, Resume.phone, Resume.skills,
                Resume.total_experience_pretty, Resume.address, Resume.file_name,
                JobCandidate.current_stage_id, JobCandidate.current_result_id,
                JobCandidate.is_active, JobCandidate.created, JobCandidate.updated,
                JobCandidate.status,
            )
            .join(Resume, JobCandidate.candidate_id == Resume.id)
            .where(JobCandidate.job_id == job_id, JobCandidate.is_active == True)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        candidates = [JobCandidateDetail(**dict(r._mapping)) for r in rows]
        return JobCandidatesResponse(total_candidates=len(candidates), candidates=candidates)

    async def get_stage_history(self, job_candidate_id: int) -> List[StageHistoryRead]:
        FromStage = aliased(MasterDropdown)
        ToStage = aliased(MasterDropdown)
        FromResult = aliased(MasterDropdown)
        ToResult = aliased(MasterDropdown)

        stmt = (
            select(
                StageHistory.id,
                StageHistory.job_candidate_id,
                FromStage.value_text.label("from_stage"),
                ToStage.value_text.label("to_stage"),
                FromResult.value_text.label("from_result"),
                ToResult.value_text.label("to_result"),
                User.full_name.label("changed_by_name"),
                StageHistory.changed_at,
            )
            .outerjoin(FromStage, StageHistory.from_stage_id == FromStage.id)
            .outerjoin(ToStage, StageHistory.to_stage_id == ToStage.id)
            .outerjoin(FromResult, StageHistory.from_result_id == FromResult.id)
            .outerjoin(ToResult, StageHistory.to_result_id == ToResult.id)
            .outerjoin(User, StageHistory.changed_by == User.id)
            .where(StageHistory.job_candidate_id == job_candidate_id)
            .order_by(StageHistory.changed_at.desc())
        )
        result = await self.db.execute(stmt)
        return [StageHistoryRead(**dict(r._mapping)) for r in result.all()]

    async def update_status(self, job_candidate_id: int, new_status: str, changed_by: int) -> JobCandidateRead:
        jc = await self.db.get(JobCandidate, job_candidate_id)
        if not jc:
            raise ValueError("Job candidate not found")
        validate_transition(jc.status, new_status)
        old_status = jc.status
        jc.status = new_status
        await self.db.flush()
        await self.db.refresh(jc)
        return JobCandidateRead.model_validate(jc)
