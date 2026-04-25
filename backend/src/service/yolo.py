import os
from PIL import Image as PILImage
from ultralytics import YOLO
from app.core.config import setting


class YoloService:
    def __init__(self, model_path: str = setting.yolo_model_path):
        self.model = YOLO(model_path)

    def predict(self, image_path: str):
        if not os.path.exists(image_path):
            return [], None

        result = self.model(image_path)[0]
        detections = []

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

        folder, filename = os.path.split(image_path)
        name, ext = os.path.splitext(filename)
        processed_path = os.path.join(folder, f"processed_{name}{ext}")

        plot_array = result.plot()
        im = PILImage.fromarray(plot_array[..., ::-1])
        im.save(processed_path)

        return detections, processed_path


yolo_service = YoloService()
