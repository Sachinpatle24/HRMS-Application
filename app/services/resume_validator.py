from typing import List
from app.models.resume_model import Resume
import json

REQUIRED_FIELDS_FOR_SEARCH = [
    "name",
    "email",
    "phone",
    "file_name",
    "skills"
]


def build_completeness_payload(resume: Resume) -> dict:
    if isinstance(resume, dict):
        return {
            "name": resume.get("name"),
            "email": resume.get("email"),
            "phone": resume.get("phone"),
            "education": resume.get("education"),
            "file_name": resume.get("file_name"),
            "skills": resume.get("skills"),
        }

    return {
        "name": resume.name,
        "email": resume.email,
        "phone": resume.phone,
        "education": resume.education,
        "file_name": resume.file_name,
        "skills": resume.skills,
    }


def is_effectively_empty(value: str) -> bool:
    try:
        data = json.loads(value)

        if isinstance(data, list):
            return not any(
                isinstance(item, dict) and any(v for v in item.values())
                for item in data
            )

        if isinstance(data, dict):
            return not any(v for v in data.values())

    except Exception:
        return False

    return False


def validate_resume_for_search(resume: dict) -> List[str]:
    missing = []
    for field in REQUIRED_FIELDS_FOR_SEARCH:
        val = resume.get(field)
        if not val or is_effectively_empty(val):
            missing.append(field)
    return missing
