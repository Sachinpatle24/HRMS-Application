from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ATS Backend"
    CORS_ORIGINS: list[str] = ["*"]
    
    PORT_NO: int = 8010
    
    # JWT Configuration
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Local Auth (hardcoded dev credentials)
    LOCAL_AUTH_USERNAME: str = "admin"
    LOCAL_AUTH_PASSWORD: str = "admin123"

    REQUIRE_DB_AT_STARTUP: bool = False

    # API endpoint for parser
    PARSE_API_ENDPOINT: str = "http://localhost:2500/parse-resume"
    
    # Database server endpoint (empty = skip DB)
    MSSQL_URL: str = ""
    RESUME_TABLE_NAME: str = "Candidate"
    RESUME_EMAIL_INDEX_NAME: str = "ux_candidate_email"
    ATTACHMENT_TABLE_NAME: str = "Attachments"
    CANDIDATE_RAW_DATA_TABLE_NAME: str = "Candidate_Raw_Data"
    RESUME_AUDITLOG_TABLE_NAME: str = "Resume_Audit_Log"
    INTERVIEW_TABLE_NAME: str = "Interviews"
    LOGIN_AUDIT_TABLE_NAME: str = "Login_Audit"

    # Job and Dropdown table names
    JOB_TABLE_NAME: str = "jobs"
    JOB_CANDIDATE_TABLE_NAME: str = "job_candidates"
    DROPDOWN_TABLE_NAME: str = "master_dropdown"
    DROPDOWN_CATEGORY_TABLE_NAME: str = "master_dropdown_category"   

    # User management table names
    USER_TABLE_NAME: str = "users"
    USER_ROLE_TABLE_NAME: str = "user_roles"
    USER_ROLE_PERMISSION_TABLE_NAME: str = "user_role_permissions"
    MENU_MASTER_TABLE_NAME: str = "menu_master"

    REPLACE_EXISTING: bool = False

    # SMTP Configuration
    SMTP_HOST: str = "smtp-mail.outlook.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True 
    DEFAULT_FROM_EMAIL: str = "noreply@example.com"

    FEEDBACK_LINK: str = "http://localhost:9012/#/feedback?interview_id={interview_id}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
