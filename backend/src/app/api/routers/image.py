from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import image_crud
from app.db.db_helper import db_helper

router = APIRouter(prefix="/image")


@router.get("/")
async def get_images(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await image_crud.get_all(session=session)


@router.post("/")
async def create_image(
    image_in: dict, session: AsyncSession = Depends(db_helper.session_dependency)
):
    return await image_crud.create(session=session, image_in=image_in)
