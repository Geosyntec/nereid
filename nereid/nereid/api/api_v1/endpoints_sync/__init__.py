from fastapi.routing import APIRouter

from nereid.api.api_v1.endpoints_sync.land_surface_loading import (
    router as land_surface_loading_router,
)
from nereid.api.api_v1.endpoints_sync.network import router as network_router
from nereid.api.api_v1.endpoints_sync.reference_data import (
    router as reference_data_router,
)
from nereid.api.api_v1.endpoints_sync.treatment_facilities import (
    router as treatment_facilities_router,
)
from nereid.api.api_v1.endpoints_sync.treatment_sites import (
    router as treatment_sites_router,
)
from nereid.api.api_v1.endpoints_sync.watershed import router as watershed_router

sync_router = APIRouter()
sync_router.include_router(network_router)
sync_router.include_router(reference_data_router)
sync_router.include_router(land_surface_loading_router)
sync_router.include_router(treatment_facilities_router)
sync_router.include_router(treatment_sites_router)
sync_router.include_router(watershed_router)
