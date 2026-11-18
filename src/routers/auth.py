from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.postgres import get_db
from ..models.Enums import AuthSignal
from ..services import AuthService
from .schemas.user import UserCreate, UserLogin, UserResponse, Token


auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["api_v1", "auth"],
)


@auth_router.post("/register", response_model=UserResponse)
async def register(user_input: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    is_valid, result_signal = await auth_service.register(user_input)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal},
        )
    return result_signal


@auth_router.post("/login", response_model=Token)
async def login(login_details: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    is_valid, result_signal = await auth_service.login(login_details)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal},
        )
    return Token(access_token = result_signal)


 