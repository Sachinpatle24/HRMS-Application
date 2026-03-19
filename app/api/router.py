# app/api/router.py
from fastapi import APIRouter, Depends
from app.auth.security import get_current_user

from app.api.v1.auth.auth_router import router as auth_router
from app.api.v1.dropdown.dropdown_router import router as dropdown_router

from app.api.v1.user.users_router import router as users_router
from app.api.v1.user.user_roles_router import router as user_roles_router
from app.api.v1.user.user_role_permissions_router import router as user_role_permissions_router

from app.api.v1.parser_router import router as parser_router
from app.api.v1.resume_router import router as resume_router

from app.api.v1.job.job_router import router as job_router
from app.api.v1.job.job_candidates_router import router as job_candidates_router
from app.api.v1.interview.interview_router import router as interview_router
from app.api.v1.interview.interviewfeedback_router import router as interviewfeedback_router
from app.api.v1.interview.interviewfeedback_page_router import router as interviewfeedback_page_router
from app.api.v1.dashboard.admin_dashboard_router import router as dashboard_router


api_router = APIRouter()

api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(parser_router, prefix="/parser", tags=["Resume Parsing"], dependencies=[Depends(get_current_user)])
api_router.include_router(resume_router, prefix="/resumes", tags=["Resume CRUD"], dependencies=[Depends(get_current_user)])
api_router.include_router(users_router,prefix="/users",tags=["Users"], dependencies=[Depends(get_current_user)])
api_router.include_router(user_roles_router,prefix="/user-roles",tags=["User Roles"], dependencies=[Depends(get_current_user)])
api_router.include_router(user_role_permissions_router,prefix="/user-role-permissions",tags=["User Role Permissions"], dependencies=[Depends(get_current_user)])
api_router.include_router(dropdown_router, prefix="/dropdowns", tags=["Dropdown Management"], dependencies=[Depends(get_current_user)])
api_router.include_router(job_router, prefix="/jobs", tags=["Job Management"], dependencies=[Depends(get_current_user)])
api_router.include_router(job_candidates_router, prefix="/job-candidates", tags=["Job Candidates"], dependencies=[Depends(get_current_user)])
api_router.include_router(interview_router, prefix="/interviews", tags=["Interviews"], dependencies=[Depends(get_current_user)])
api_router.include_router(interviewfeedback_router, prefix="/interviews", tags=["Interview Feedback"])
api_router.include_router(interviewfeedback_page_router, prefix="/interviews/feedback-page", tags=["Interview FeedbackPage Public Routes"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard Admin"], dependencies=[Depends(get_current_user)])
