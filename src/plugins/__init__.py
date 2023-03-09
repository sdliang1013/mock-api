from core.router import DeferredAPIRouter
from plugins.ryd.api import router as rdb_router

api_router = DeferredAPIRouter()

api_router.include_router(explorer_router, prefix="/explorer", tags=["explorer"])
api_router.include_router(rdb_router, prefix="/rdb", tags=["rdb"])
api_router.include_router(redis_router, prefix="/redis", tags=["redis"])
