from fastapi import APIRouter

from app.routes.auth_router import router as auth_router
from app.routes.pet_router import router as pet_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(pet_router)
