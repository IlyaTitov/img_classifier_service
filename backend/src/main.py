from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.api import router
from app.models.base import Base


from app.db.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Созадана бд")
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
