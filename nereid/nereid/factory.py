from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles


from nereid.api.api_v1.endpoints_sync import sync_router

from nereid.api.api_v1.endpoints import api_router
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.cache import redis_cache
from nereid.core.config import settings
from nereid.src import tasks as tasks


def create_app(settings_override: Optional[Dict[str, Any]] = None) -> FastAPI:

    _settings = settings.copy()

    if settings_override is not None:
        _settings.update(settings_override)

    app = FastAPI(
        title="nereid", version=_settings.VERSION, docs_url=None, redoc_url=None
    )

    app.tasks = tasks
    # if not _settings.FORCE_FOREGROUND:
    #     import nereid.bg_worker as tasks

    #     app.tasks = tasks

    static_path = _settings._nereid_path / "static"
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

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
        except Exception as e:  # pragma: no cover
            pass

        context = get_valid_context(state, region)

        return context

    app.include_router(sync_router, prefix=_settings.API_V1_STR)
    app.include_router(api_router, prefix=_settings.API_V1_STR + "/bg")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.ALLOW_CORS_ORIGINS,
        allow_origin_regex=_settings.ALLOW_CORS_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS", "POST"],
        allow_headers=["*"],
    )

    return app
