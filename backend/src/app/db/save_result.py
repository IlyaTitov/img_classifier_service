from sqlalchemy.orm import Session
from typing import List
from app.models.detection import Detection
from app.models.image import Image


def save_result(
    session: Session, detections: List[dict], processed_path: str, image_id: int
):

    image = session.get(Image, image_id)
    if image:
        image.processed_path = processed_path

    for det in detections:
        db_det = Detection(
            image_id=image_id,
            object_type_id=det["class_id"],
            x_min=det["x_min"],
            y_min=det["y_min"],
            x_max=det["x_max"],
            y_max=det["y_max"],
            confidence=det["confidence"],
        )
        session.add(db_det)
