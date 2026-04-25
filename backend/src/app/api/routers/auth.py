from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schemas.user import UserLogin, UserCreate, Token
from app.db.db_helper import db_helper
from app.models.user import User
from service import auth_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, session: AsyncSession = Depends(db_helper.session_dependency)
):
    user = await auth_service.authenticate_user(
        session, user_data.login, user_data.password
    )

    access_token = await auth_service.create_token_for_user(user)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(db_helper.session_dependency)
):
    user = await auth_service.register_new_user(session, user_data)
    return {
        "message": "Пользователь успешно зарегистрирован",
        "username": user.login,
    }
