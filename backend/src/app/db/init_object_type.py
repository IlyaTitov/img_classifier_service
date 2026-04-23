from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.detection import ObjectType


async def init_object_type(session_factory, class_names: dict):
    async with session_factory() as session:
        stmt = select(ObjectType).limit(1)
        r = await session.execute(stmt)
        if r is not None:
            return

        for c_id, name in class_names.items():
            session.add(ObjectType(id=c_id, name=name))

        await session.commit()
