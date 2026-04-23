from celery import Celery
import time


celery_app = Celery(
    "task", broker="redis://localhost:6379/0", include="src.tasks.image_tasks"
)
