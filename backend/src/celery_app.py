from celery import Celery
from app.core.config import setting

celery_app = Celery(
    "img_classifier",
    broker=setting.celery_broker_url,
    include=["tasks.image_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
