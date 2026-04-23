from fastapi import APIRouter
from .routers.image import router as router_image
from .routers.detection import router as router_detection

router = APIRouter(prefix="/v1")
router.include_router(router_image, prefix="/image")
router.include_router(router_detection, prefix="/detection")
