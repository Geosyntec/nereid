from fastapi import APIRouter

from nereid.api.api_v1.endpoints_async.land_surface_loading import (
    router as land_surface_loading_router,
)
from nereid.api.api_v1.endpoints_async.network import router as network_router
from nereid.api.api_v1.endpoints_async.reference_data import (
    router as reference_data_router,
)
from nereid.api.api_v1.endpoints_async.tasks import router as task_router
from nereid.api.api_v1.endpoints_async.treatment_facilities import (
    router as treatment_facilities_router,
)
from nereid.api.api_v1.endpoints_async.treatment_sites import (
    router as treatment_sites_router,
)
from nereid.api.api_v1.endpoints_async.watershed import router as watershed_router

async_router = APIRouter()
async_router.include_router(network_router)
async_router.include_router(reference_data_router)
async_router.include_router(land_surface_loading_router)
async_router.include_router(treatment_facilities_router)
async_router.include_router(treatment_sites_router)
async_router.include_router(watershed_router)
async_router.include_router(task_router)
