from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database.postgres import get_db 
from .helpers.security import verify_access_token
from  .models.Enums import AuthSignal
from  .models.mini_rag_postgres.schemas import User

# tokenUrl must match the login endpoint, so the Authorize button in /docs works
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=AuthSignal.TOKEN_INVALID_OR_EXPIRED.value,
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. verify the JWT and extract the user id (the "sub" claim)
    user_id = verify_access_token(token)
    if user_id is None:
        raise credentials_exception

    # the token stores the id as a string, the column is a UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    # 2. fetch the user from the database
    result = await db.execute(select(User).where(User.user_id == user_uuid))
    user = result.scalar_one_or_none()

    # 3. the user may have been deleted after the token was issued
    if user is None:
        raise credentials_exception

    return user 

  
