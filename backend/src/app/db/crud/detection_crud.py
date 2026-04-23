from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.models.detection import Detection


async def get_detections(session: AsyncSession) -> List[Detection]:
    stmt = select(Detection).order_by(Detection.id)
    r = await session.execute(stmt)
    return list(r.scalars().all())
