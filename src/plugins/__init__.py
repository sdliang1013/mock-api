from core.router import DeferredAPIRouter
from plugins.ryd.api import router as ryd_router

api_router = DeferredAPIRouter()

api_router.include_router(ryd_router, prefix="/ryd", tags=["ryd"])
