from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select
from app.db.db_helper import db_helper
from app.models.user import User


async def get_all(session: AsyncSession = Depends(db_helper.session_dependency)):
    stmt = select(User).order_by()
    r = await session.execute(stmt)
    return r.scalars().all()
