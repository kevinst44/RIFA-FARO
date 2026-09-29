from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from jose import jwt
from models import LoginRequest, TokenResponse
from config import settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    if request.username != settings.ADMIN_USERNAME or request.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    token_data = {"sub": request.username, "exp": expire}
    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return TokenResponse(access_token=token)


@router.post("/verify")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return {"valid": True, "username": payload["sub"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
