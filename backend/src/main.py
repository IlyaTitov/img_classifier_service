from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import router
from app.models.base import Base
from app.core.config import setting
from app.db.db_helper import db_helper
from app.db.init_object_type import init_object_type
from service.yolo import yolo_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("БД создана/проверена")

    class_names = yolo_service.model.names
    await init_object_type(
        session_factory=db_helper.session_factory, class_names=class_names
    )

    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(setting.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=setting.upload_dir), name="uploads")

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
