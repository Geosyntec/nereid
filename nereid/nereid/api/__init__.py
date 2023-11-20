from fastapi import APIRouter

from .api_v1.endpoints_async import async_router as async_router_v1
from .api_v1.endpoints_sync import sync_router as sync_router_v1

async_router = APIRouter(prefix="/api")
async_router.include_router(async_router_v1)

sync_router = APIRouter(prefix="/api")
sync_router.include_router(sync_router_v1)
