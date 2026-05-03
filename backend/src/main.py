import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import router
from app.core.cache import close_cache, init_cache
from app.core.config import setting
from app.db.db_helper import db_helper
from app.db.init_object_type import init_object_type
from app.models.base import Base
from service.yolo import yolo_service

_LOG_DIR = os.path.join(setting.upload_dir, "..", "logs")
_LOG_DIR = os.path.normpath(_LOG_DIR)
os.makedirs(_LOG_DIR, exist_ok=True)

_fmt = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
_datefmt = "%Y-%m-%dT%H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=_fmt,
    datefmt=_datefmt,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(_LOG_DIR, "app.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("img_classifier.http")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.getLogger("img_classifier").info("БД создана/проверена")

    class_names = yolo_service.model.names
    await init_object_type(
        session_factory=db_helper.session_factory, class_names=class_names
    )

    await init_cache()
    logging.getLogger("img_classifier").info("Redis-кэш инициализирован")

    yield

    await close_cache()
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t_start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - t_start) * 1000
    content_length = request.headers.get("content-length", "-")

    logger.info(
        "method=%s path=%s status=%d duration_ms=%.1f content_length=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        content_length,
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(setting.upload_dir, exist_ok=True)
os.makedirs(setting.originals_dir, exist_ok=True)
os.makedirs(setting.processed_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=setting.upload_dir), name="uploads")

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
