from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.core.config import setting


def _make_sync_url(async_url: str) -> str:
    """Гарантированно превращает любой URL в синхронный для Postgres или SQLite."""
    # 1. Если это Postgres (асинхронный или обычный), делаем его через psycopg2
    if "postgresql" in async_url:
        # Убираем любой драйвер и ставим psycopg2
        base = async_url.split("://")[1]
        return f"postgresql+psycopg2://{base}"

    # 2. Если это SQLite (для тестов)
    if "sqlite" in async_url:
        return async_url.replace("+aiosqlite", "")

    return async_url


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False, autocommit=False
        )
        sync_url = _make_sync_url(url)
        self.sync_engine = create_engine(url=sync_url, echo=echo)
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


db_helper = DatabaseHelper(setting.database_url, setting.database_echo)
