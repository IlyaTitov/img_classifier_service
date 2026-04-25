import asyncio

from app.db.db_helper import db_helper
from app.models.image import Image
from app.models.base import Base


async def run():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Готово!")


if __name__ == "__main__":
    asyncio.run(run())
