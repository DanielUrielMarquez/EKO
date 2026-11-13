from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import InMemoryRateLimiter
from app.core.tokens import create_access_token
from app.models import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import authenticate_user, create_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])

login_limiter = InMemoryRateLimiter(
    limit=settings.RATE_LIMIT_LOGIN_ATTEMPTS,
    window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS,
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: UserRegister, db: Session = Depends(get_db)):
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(724193)"))

    users_count = db.scalar(select(func.count()).select_from(User))

    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El registro está cerrado.",
        )

    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la cuenta.",
        )

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: UserLogin,
    http_request: Request,
    db: Session = Depends(get_db),
):
    client_ip = http_request.client.host if http_request.client else "unknown"
    login_limiter.check(client_ip)

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        login_limiter.record_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_limiter.reset_key(client_ip)
    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token)
