from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import detection_crud
from app.db.db_helper import db_helper

router = APIRouter()


@router.get("/")
async def get_detections(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await detection_crud.get_detections(session=session)
