from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.image import Image


async def get_all(session: AsyncSession) -> List[Image]:
    stmt = select(Image).order_by(Image.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create(session: AsyncSession, image_in) -> Image:
    new_image = Image(**image_in.model_dump())
    session.add(new_image)
    await session.commit()
    await session.refresh()
    return new_image
