from fastapi import APIRouter
from .routers.image import router as router_image
from .routers.detection import router as router_detection
from .routers.user import router as router_user
from .routers.auth import router as router_auth

router = APIRouter(prefix="/v1")
router.include_router(router_image, prefix="/image")
router.include_router(router_detection, prefix="/detection")
router.include_router(router_user, prefix="/user")
router.include_router(router_auth, prefix="/auth")
