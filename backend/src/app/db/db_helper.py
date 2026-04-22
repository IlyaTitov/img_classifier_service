from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import setting


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False, autocommit=False
        )

    async def dispose(self):
        await self.engine.dispose()

    async def session_dependency(self) -> AsyncGenerator:
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(setting.datebase_url, setting.datebase_echo)
