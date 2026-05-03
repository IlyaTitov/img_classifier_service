from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.detection import Detection
from app.models.image import Image


async def get_all(session: AsyncSession) -> List[Image]:
    stmt = select(Image).order_by(Image.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create(
    session: AsyncSession,
    name: str,
    original_path: str,
    user_id: int,
    file_size: Optional[int],
) -> Image:
    new_image = Image(
        name=name,
        original_path=original_path,
        user_id=user_id,
        file_size=file_size,
    )
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image


async def set_task_id(session: AsyncSession, image_id: int, task_id: str) -> None:
    """Сохраняет идентификатор Celery-задачи после постановки в очередь."""
    image = await session.get(Image, image_id)
    if image:
        image.task_id = task_id
        await session.commit()


async def get_by_id(session: AsyncSession, image_id: int) -> Optional[Image]:
    stmt = (
        select(Image)
        .where(Image.id == image_id)
        .options(selectinload(Image.detections).selectinload(Detection.object_type))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_status(session: AsyncSession, image_id: int) -> Optional[Image]:
    """Загружает только поля Image без JOIN детекций — для лёгкого endpoint'а статуса."""
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_archive(
    session: AsyncSession,
    user_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    order_col = (
        Image.detection_count if sort_by == "detection_count" else Image.created_at
    )
    stmt = (
        select(Image)
        .where(Image.user_id == user_id)
        .order_by(order_col.asc() if order == "asc" else order_col.desc())
        .limit(limit)
        .offset(offset)
    )

    if date_from:
        stmt = stmt.where(Image.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        stmt = stmt.where(Image.created_at <= datetime.combine(date_to, time.max))

    result = await session.execute(stmt)
    rows = result.scalars().all()

    return [
        {
            "id": img.id,
            "task_id": img.task_id,
            "name": img.name,
            "created_at": img.created_at.isoformat() if img.created_at else None,
            "processing_complete": img.processed_path is not None,
            "processed_filename": img.processed_path,
            "original_filename": img.original_path,
            "detection_count": img.detection_count,
            "file_size": img.file_size,
            "processing_duration_ms": img.processing_duration_ms,
        }
        for img in rows
    ]
