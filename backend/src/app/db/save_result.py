from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.detection import Detection
from app.models.image import Image


def save_result(
    session: Session,
    detections: List[dict],
    processed_path: Optional[str],
    image_id: int,
    processing_duration_ms: Optional[int] = None,
) -> None:
    image = session.get(Image, image_id)
    if image:
        image.processed_path = processed_path
        image.processing_duration_ms = processing_duration_ms
        image.detection_count = len(detections)

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
