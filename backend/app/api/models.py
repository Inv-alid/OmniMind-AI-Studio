from fastapi import APIRouter
from app.core.router import router

router_api = APIRouter()

# Fix naming collision
router = router_api


@router.get("/")
async def list_models():
    return {"models": router.list_models()}
