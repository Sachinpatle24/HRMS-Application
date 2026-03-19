from fastapi import APIRouter

from app.api.v1.interview.interview_router import get_candidate_interview_history
from app.api.v1.resume_router import download_resume
from app.api.v1.dropdown.dropdown_router import get_dropdown_options

router = APIRouter()

router.add_api_route("/candidates/{candidate_id}/interview-history", get_candidate_interview_history, methods=["GET"])
router.add_api_route("/resumes/download/{candidate_id}", download_resume, methods=["GET"])
router.add_api_route("/dropdowns/{category}", get_dropdown_options, methods=["GET"])
