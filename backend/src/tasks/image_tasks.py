from app.db.db_helper import db_helper

from celery_app import celery_app
from service.yolo import yolo_service
from app.db.save_result import save_result
from app.models.image import Image


@celery_app.task(name="tasks.image_tasks.process_img")
def process_img(image_id: int):
    with db_helper.get_session_factory() as session:
        image = session.get(Image, image_id)
        if image is None:
            return f"Ошибка: Изображение с ID {image_id} не найдено"
        detections, processed_path = yolo_service.predict(image.original_path)
        save_result(
            session=session,
            detections=detections,
            processed_path=processed_path,
            image_id=image_id,
        )
        session.commit()
    return f"Успешно обработано изображение ID {image_id}"
