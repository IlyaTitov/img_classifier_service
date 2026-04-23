from ultralytics import YOLO
import os
from PIL import Image as PILImage


class YoloService:
    def __init__(
        self,
        model_path: str = "D:/img_classifier_service/backend/src/weights/yolov8s.pt",
    ):
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
        processed_path = os.path.join(folder, f"processed_{filename}")

        plot_array = result.plot()
        im = PILImage.fromarray(plot_array[..., ::-1])
        im.save(processed_path)

        return detections, processed_path


yolo_service = YoloService()
