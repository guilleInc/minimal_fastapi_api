from fastapi import APIRouter

from app.routes.pet_router import router as pet_router

router = APIRouter()
router.include_router(pet_router)
