import logging
import os
import time

from celery_app import celery_app
from app.core.config import setting
from app.db.db_helper import db_helper
from app.db.save_result import save_result
from app.models.image import Image
from service.yolo import yolo_service

logger = logging.getLogger("img_classifier.worker")


@celery_app.task(name="tasks.image_tasks.process_img")
def process_img(image_id: int) -> str:
    with db_helper.get_session_factory() as session:
        image = session.get(Image, image_id)
        if image is None:
            logger.error("image_id=%d не найдено в БД", image_id)
            return f"Ошибка: Изображение с ID {image_id} не найдено"

        original_abs = os.path.join(setting.upload_dir, image.original_path)

        t_start = time.perf_counter()
        detections, processed_abs = yolo_service.predict(
            image_path=original_abs,
            processed_dir=setting.processed_dir,
        )
        duration_ms = int((time.perf_counter() - t_start) * 1000)

        processed_rel: str | None = None
        if processed_abs:
            processed_rel = os.path.relpath(processed_abs, setting.upload_dir).replace(
                "\\", "/"
            )

        labels = [d["class_id"] for d in detections]
        logger.info(
            "image_id=%d file=%s duration_ms=%d detections=%d classes=%s",
            image_id,
            image.original_path,
            duration_ms,
            len(detections),
            labels,
        )

        save_result(
            session=session,
            detections=detections,
            processed_path=processed_rel,
            image_id=image_id,
            processing_duration_ms=duration_ms,
        )
        session.commit()

    return f"Успешно обработано изображение ID {image_id}, duration_ms={duration_ms}"
