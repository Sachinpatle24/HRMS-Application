import json

def safe_json_dumps(obj, default=None):
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return json.dumps(default if default is not None else [])
        
def normalize_parser_output(parsed_data: dict) -> dict:
    parsed = parsed_data.copy()
    
    # 1. Early exit on parser failure
    if not parsed.get("success"):
        return {
            "file_name": parsed.get("file_name"),
        }

    # 2. Structured payload
    structured = parsed.get("data", {})

    # 3. Helpers
    def first_or_none(value):
        if not value:
            return None
        
        if isinstance(value, str):
            return value.strip() or None
        
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    return item.strip()
                if isinstance(item, dict):
                    for key in ("value", "email", "url", "phone"):
                        v = item.get(key)
                        if isinstance(v, str) and v.strip():
                            return v.strip()
                if isinstance(item, list):
                    for sub in item:
                        if isinstance(sub, str) and sub.strip():
                            return sub.strip()
            return None
        
        return None

    def str_or_none(value):
        if not value:
            return None

        collected = []

        def collect(item):
            if not item:
                return

            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str) and name.strip():
                    collected.append(name.strip())

            elif isinstance(item, str):
                if item.strip():
                    collected.append(item.strip())

            elif isinstance(item, list):
                for sub in item:
                    collect(sub)

        if isinstance(value, list):
            for v in value:
                collect(v)
        else:
            collect(value)

        return ", ".join(collected) if collected else None

    # Email normalization
    email = first_or_none(structured.get("emails"))
    email = email.strip().lower() if isinstance(email, str) and email.strip() else None
    
    # 5. Final payload
    return {
        "name": structured.get("name") or None,
        "email": email,           
        "phone": first_or_none(structured.get("phoneNumbers")),      
        "address": safe_json_dumps(structured.get("addresses", [])),
        "website": first_or_none(structured.get("websites")),      
        "date_of_birth": structured.get("dateOfBirth") or None,
        "summary": structured.get("summary") or None,
        "education": safe_json_dumps(structured.get("education", [])),
        "work_experience": safe_json_dumps(structured.get("workExperience", [])),
        "skills": str_or_none(structured.get("skills")),
        "certifications": str_or_none(structured.get("certifications")),
        "projects": str_or_none(structured.get("projects")),
        "file_name": parsed.get("file_name"),
        "created_by": parsed.get("created_by"),
    }
