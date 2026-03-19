from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError
from uuid import uuid4
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security = HTTPBearer()


def create_access_token(data: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)).timestamp()),
        "iss": "ats-backend",
        "aud": "ats-api",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience="ats-api",
            issuer="ats-backend",
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    payload["username"] = payload.get("sub")
    return payload
