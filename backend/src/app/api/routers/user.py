from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_helper import db_helper

from app.db.crud import user_crud

router = APIRouter()


@router.get("/")
async def get_users(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await user_crud.get_all(session=session)
