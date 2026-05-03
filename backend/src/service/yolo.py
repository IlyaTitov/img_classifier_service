import os
from typing import Optional

from PIL import Image as PILImage
from ultralytics import YOLO

from app.core.config import setting

# Форматы, которые гарантированно читает Pillow / OpenCV (через Ultralytics)
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tiff",
    ".tif",
    ".webp",
    ".avif",
}


class YoloService:
    def __init__(self, model_path: str = setting.yolo_model_path):
        self.model = YOLO(model_path)

    def predict(
        self,
        image_path: str,
        processed_dir: Optional[str] = None,
    ) -> tuple[list[dict], Optional[str]]:

        if not os.path.exists(image_path):
            return [], None

        _, ext = os.path.splitext(image_path)
        if ext.lower() not in SUPPORTED_EXTENSIONS:
            return [], None

        result = self.model(image_path)[0]
        detections: list[dict] = []

        for box in result.boxes:
            coords = box.xyxy[0].tolist()
            detections.append(
                {
                    "class_id": int(box.cls),
                    "confidence": float(box.conf),
                    "x_min": coords[0],
                    "y_min": coords[1],
                    "x_max": coords[2],
                    "y_max": coords[3],
                }
            )

        _, filename = os.path.split(image_path)
        name, ext = os.path.splitext(filename)
        out_dir = processed_dir if processed_dir else os.path.dirname(image_path)
        os.makedirs(out_dir, exist_ok=True)

        processed_path = os.path.join(out_dir, f"processed_{name}{ext}")
        plot_array = result.plot()
        PILImage.fromarray(plot_array[..., ::-1]).save(processed_path)

        return detections, processed_path


yolo_service = YoloService()
