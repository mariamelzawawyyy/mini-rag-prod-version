from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..helpers.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from ..routers.schemas.user import UserCreate, UserLogin
from ..models.mini_rag_postgres.schemas.User import User
from ..models.Enums import AuthSignal
 
  
class AuthService:
    """Handles user signup and login.

    Methods return (success, result): on failure the result is a message
    from AuthSignal, on success it is the user (signup) or the token (login).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # 1. Signup Flow
    async def register(self, user_input: UserCreate):
        # التأكد من الإيميل
        email_result = await self.db.execute(
            select(User).where(User.email == user_input.email)
        )
        if email_result.scalar_one_or_none():
            return False, AuthSignal.EMAIL_ALREADY_EXISTS.value

        # التأكد من اليوزرنيم
        username_result = await self.db.execute(
            select(User).where(User.username == user_input.username)
        )
        if username_result.scalar_one_or_none():
            return False, AuthSignal.USERNAME_ALREADY_TAKEN.value

        # إنشاء وحفظ اليوزر الجديد
        new_user = User(
            username=user_input.username,
            email=user_input.email,
            hashed_password=hash_password(user_input.password),
        )
        self.db.add(new_user)

        try:
            await self.db.commit()
        except IntegrityError:
            # two requests signed up with the same email/username at the same time
            await self.db.rollback()
            return False, AuthSignal.EMAIL_ALREADY_EXISTS.value

        await self.db.refresh(new_user)
        return True, new_user

    # 2. Login Flow
    async def login(self, login_details: UserLogin):
        result = await self.db.execute(
            select(User).where(User.email == login_details.email)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False, AuthSignal.INVALID_CREDENTIALS.value

        # الباسورد غلط
        if not verify_password(login_details.password, user.hashed_password):
            return False, AuthSignal.INVALID_CREDENTIALS.value

        # إنشاء التوكن
        access_token = create_access_token({"sub": str(user.user_id)})
        return True, access_token 
 
 








