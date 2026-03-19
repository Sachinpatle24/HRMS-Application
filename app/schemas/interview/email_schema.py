from pydantic import BaseModel, EmailStr
from typing import List

class EmailRequest(BaseModel):
    from_email: EmailStr
    to_emails: List[EmailStr]
    cc_emails: List[EmailStr] = []
    bcc_emails: List[EmailStr] = []
    subject: str
    body: str
