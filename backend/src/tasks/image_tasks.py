from src.celery_app import celery_app
from src.service.yolo import yolo_service


@celery_app.task
def process_img(image_path: str):
    detections = yolo_service.predict(image_path)
    return f"Обработано фото {image_path} найдено {len(detections)}"


process_img.delay("D:/img_classifier_service/4476862-hd_1920_1080_30fps_00_00_00_1.png")
