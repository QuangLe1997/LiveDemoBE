from fastapi import APIRouter

from .get_delaytime import router as delay_time_router

router = APIRouter()
router.include_router(delay_time_router)
