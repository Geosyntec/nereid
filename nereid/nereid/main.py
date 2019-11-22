from fastapi import FastAPI

from nereid.api.api_v1.api import api_router
from nereid.core import config

app = FastAPI()

app.include_router(api_router, prefix=config.API_V1_STR)
