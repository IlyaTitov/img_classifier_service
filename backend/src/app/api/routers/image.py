import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.crud import image_crud
from src.app.db.db_helper import db_helper
from src.tasks.image_tasks import process_img
from src.app.core.config import setting

router = APIRouter(prefix="/image")


@router.get("/")
async def get_images(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await image_crud.get_all(session=session)


@router.post("/")
async def create_image(
    image_in: dict, session: AsyncSession = Depends(db_helper.session_dependency)
):
    return await image_crud.create(session=session, image_in=image_in)


@router.post("/upload")
async def upload(
    file: UploadFile = File(),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    file_path = os.path.join(setting.upload_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    new_image = await image_crud.create(
        session=session, name=file.filename, original_path=file_path
    )

    process_img.delay(image_id=new_image.id)

    return new_image
