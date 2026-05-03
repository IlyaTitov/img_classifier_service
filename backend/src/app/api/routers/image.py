import os
import shutil
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import IMAGE_TTL_DONE, IMAGE_TTL_PENDING, cache_get, cache_set
from app.core.config import setting
from app.db.crud import image_crud
from app.db.db_helper import db_helper
from app.models.user import User
from service.auth_service import get_current_user
from tasks.image_tasks import process_img

router = APIRouter()

_ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tiff",
    ".tif",
    ".webp",
    ".avif",
}

_DEFAULT_PAGE_SIZE = 50
_MAX_PAGE_SIZE = 200


def _image_response(image, detections=None):
    return {
        "id": image.id,
        "task_id": image.task_id,
        "name": image.name,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "processing_complete": image.processed_path is not None,
        "processed_filename": image.processed_path,
        "original_filename": image.original_path,
        "processing_duration_ms": image.processing_duration_ms,
        "detections": detections or [],
    }


@router.get("/all")
async def get_all_images(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await image_crud.get_all(session=session)


@router.get("/")
async def get_images(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|detection_count)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(_DEFAULT_PAGE_SIZE, ge=1, le=_MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
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
        limit=limit,
        offset=offset,
    )


@router.post("/upload")
async def upload(
    file: UploadFile = File(),
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Допускаются только изображения")

    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла '{ext}'. "
            f"Допустимы: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    os.makedirs(setting.originals_dir, exist_ok=True)
    abs_path = os.path.join(setting.originals_dir, file.filename)
    try:
        with open(abs_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    file_size: Optional[int] = file.size

    relative_path = os.path.join("originals", file.filename).replace("\\", "/")

    new_image = await image_crud.create(
        session=session,
        name=file.filename,
        original_path=relative_path,
        user_id=current_user.id,
        file_size=file_size,
    )

    task = process_img.delay(image_id=new_image.id)
    await image_crud.set_task_id(session, new_image.id, task.id)
    new_image.task_id = task.id

    return _image_response(new_image)


@router.get("/{image_id}/status")
async def get_image_status(
    image_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):

    image = await image_crud.get_status(session=session, image_id=image_id)
    if image is None or image.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Изображение не найдено")

    done = image.processed_path is not None
    response: dict = {
        "id": image.id,
        "task_id": image.task_id,
        "processing_complete": done,
    }
    if not done:
        response["retry_after"] = 2

    return response


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):

    cache_key = f"image_detail:{image_id}:{current_user.id}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

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

    result = _image_response(image, detections)
    ttl = IMAGE_TTL_DONE if image.processed_path is not None else IMAGE_TTL_PENDING
    await cache_set(cache_key, result, ttl)

    return result
