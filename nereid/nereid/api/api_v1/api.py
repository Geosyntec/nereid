from fastapi import APIRouter

from nereid.api.api_v1.endpoints.network import router as network_router
from nereid.api.api_v1.endpoints.reference_data import router as reference_data_router
from nereid.api.api_v1.endpoints.land_surface_loading import (
    router as land_surface_loading_router,
)


api_router = APIRouter()
api_router.include_router(network_router)
api_router.include_router(reference_data_router)
api_router.include_router(land_surface_loading_router)
