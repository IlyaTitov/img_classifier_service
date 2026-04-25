from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.models.user import User
from app.core.auth import verify_password, create_access_token, hash_password
from app.core.config import setting
from app.api.schemas.user import UserCreate
from app.db.db_helper import db_helper

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


async def authenticate_user(session: AsyncSession, login: str, password: str) -> User:
    stmt = select(User).where(User.login == login)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def create_token_for_user(user: User) -> str:
    return create_access_token(data={"sub": str(user.id)})


async def register_new_user(session: AsyncSession, user_data: UserCreate) -> User:
    hashed = hash_password(user_data.password)
    new_user = User(login=user_data.login, hashed_password=hashed, is_active=True)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == int(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user
