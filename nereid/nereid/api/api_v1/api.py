from fastapi import APIRouter

from nereid.api.api_v1.endpoints.network import router as network_router
from nereid.api.api_v1.endpoints.reference_data import router as reference_data_router


api_router = APIRouter()
api_router.include_router(network_router)
api_router.include_router(reference_data_router)
