import os
import shutil
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import setting
from app.db.crud import image_crud
from app.db.db_helper import db_helper
from app.models.user import User
from service.auth_service import get_current_user
from tasks.image_tasks import process_img

router = APIRouter()


def _image_response(image, detections=None):
    return {
        "id": image.id,
        "name": image.name,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "processing_complete": image.processed_path is not None,
        "processed_filename": (
            os.path.basename(image.processed_path) if image.processed_path else None
        ),
        "original_filename": os.path.basename(image.original_path),
        "detections": detections or [],
    }


@router.get("/")
async def get_images(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|detection_count)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    return await image_crud.get_archive(
        session=session,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        order=order,
    )


@router.post("/upload")
async def upload(
    file: UploadFile = File(),
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Допускаются только изображения")

    os.makedirs(setting.upload_dir, exist_ok=True)
    file_path = os.path.join(setting.upload_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    new_image = await image_crud.create(
        session=session,
        name=file.filename,
        original_path=file_path,
        user_id=current_user.id,
    )

    process_img.delay(image_id=new_image.id)

    return _image_response(new_image)


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    image = await image_crud.get_by_id(session=session, image_id=image_id)
    if image is None or image.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Изображение не найдено")

    detections = [
        {
            "id": d.id,
            "label": (d.object_type.name if d.object_type else str(d.object_type_id)),
            "confidence": d.confidence,
            "x_min": d.x_min,
            "y_min": d.y_min,
            "x_max": d.x_max,
            "y_max": d.y_max,
        }
        for d in image.detections
    ]

    return _image_response(image, detections)
