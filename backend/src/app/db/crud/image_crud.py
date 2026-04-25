from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.detection import Detection
from app.models.image import Image


async def get_all(session: AsyncSession) -> List[Image]:
    stmt = select(Image).order_by(Image.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create(
    session: AsyncSession, name: str, original_path: str, user_id: int
) -> Image:
    new_image = Image(name=name, original_path=original_path, user_id=user_id)
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image


async def get_by_id(session: AsyncSession, image_id: int) -> Optional[Image]:
    stmt = (
        select(Image)
        .where(Image.id == image_id)
        .options(selectinload(Image.detections).selectinload(Detection.object_type))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_archive(
    session: AsyncSession,
    user_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> List[dict]:
    det_count = func.count(Detection.id)
    stmt = (
        select(Image, det_count.label("detection_count"))
        .outerjoin(Detection, Detection.image_id == Image.id)
        .where(Image.user_id == user_id)
        .group_by(Image.id)
    )

    if date_from:
        stmt = stmt.where(Image.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        stmt = stmt.where(Image.created_at <= datetime.combine(date_to, time.max))

    order_col = det_count if sort_by == "detection_count" else Image.created_at
    stmt = stmt.order_by(order_col.asc() if order == "asc" else order_col.desc())

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "id": img.id,
            "name": img.name,
            "created_at": img.created_at.isoformat() if img.created_at else None,
            "processing_complete": img.processed_path is not None,
            "processed_filename": _basename(img.processed_path),
            "original_filename": _basename(img.original_path),
            "detection_count": count,
        }
        for img, count in rows
    ]


def _basename(path: Optional[str]) -> Optional[str]:
    if path is None:
        return None
    import os

    return os.path.basename(path)
