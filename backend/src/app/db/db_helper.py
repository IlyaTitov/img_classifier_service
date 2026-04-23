from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from src.app.core.config import setting


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False, autocommit=False
        )
        sync_url = url.replace("sqlite+aiosqlite", "sqlite")
        self.sync_engine = create_engine(url=sync_url)
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine, autoflush=False, expire_on_commit=False
        )

    async def dispose(self):
        await self.engine.dispose()

    async def session_dependency(self) -> AsyncGenerator:
        async with self.session_factory() as session:
            yield session

    def get_session_factory(self):
        return self.sync_session_factory()


db_helper = DatabaseHelper(setting.datebase_url, setting.datebase_echo)
