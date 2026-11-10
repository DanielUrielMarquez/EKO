from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.core.tokens import create_access_token
from app.models import User
from app.schemas.auth import (
    TokenResponse,
    UserRegister,
    UserResponse,
    UserLogin,
)
from app.services.auth_service import authenticate_user, create_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserRegister,
    db: Session = Depends(get_db),
):
    if db.get_bind().dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(724193)")
        )
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
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token)