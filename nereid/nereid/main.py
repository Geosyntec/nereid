from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

import nereid
from nereid.api.api_v1.api import api_router
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.cache import redis_cache
from nereid.core.config import settings

app = FastAPI(title="nereid", version=nereid.__version__, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="nereid/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=str(app.openapi_url),
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/logo/trident_neptune_logo.ico",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=str(app.openapi_url),
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/logo/trident_neptune_logo.ico",
    )


@app.get("/config", include_in_schema=False)
async def check_config(state="state", region="region"):

    try:  # pragma: no cover
        # if redis is available, let's flush the cache to start
        # fresh.
        if redis_cache.ping():
            redis_cache.flushdb()
    except:  # pragma: no cover
        pass

    context = get_valid_context(state, region)

    return context


app.include_router(api_router, prefix=settings.API_V1_STR)
# origins = [
#     "http://localhost:8000",
#     "http://localhost:5500",
# ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_CORS_ORIGINS,
    allow_origin_regex=settings.ALLOW_CORS_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS", "POST"],
    allow_headers=["*"],
)
