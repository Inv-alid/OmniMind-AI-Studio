from fastapi import APIRouter
from app.core.router import router as model_router

api = APIRouter()


@api.get("/")
async def list_models():
    return {"models": model_router.list_models()}
