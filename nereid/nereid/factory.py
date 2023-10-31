from typing import Any

from brotli_asgi import BrotliMiddleware
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles

from nereid.api.api_v1.endpoints_sync import sync_router
from nereid.api.api_v1.utils import get_valid_context
from nereid.api.docs import get_better_swagger_ui_html
from nereid.core.config import nereid_path, settings
from nereid.core.log import logging

logger = logging.getLogger(__name__)


def create_app(
    *,
    settings_override: dict[str, Any] | None = None,
    app_kwargs: dict[str, Any] | None = None,
) -> FastAPI:
    _settings = settings.model_copy(deep=True)
    _settings.update(settings_override or {})

    kwargs = app_kwargs or {}

    app = FastAPI(
        title="nereid",
        version=_settings.VERSION,
        docs_url=None,
        redoc_url=None,
        **kwargs,
    )
    app._settings = _settings  # type: ignore
    app._context_cache = {}  # type: ignore

    static_path = nereid_path / "static"
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    if _settings.ASYNC_MODE == "replace":  # pragma: no cover
        from nereid.api.api_v1.endpoints_async import async_router

        app.include_router(async_router, prefix=_settings.API_V1_STR, tags=["async"])
    else:
        app.include_router(sync_router, prefix=_settings.API_V1_STR)
        if _settings.ASYNC_MODE == "add":  # pragma: no cover
            from nereid.api.api_v1.endpoints_async import async_router

            app.include_router(
                async_router,
                prefix=_settings.API_V1_STR + _settings.ASYNC_ROUTE_PREFIX,
                tags=["async"],
            )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        kwargs: dict[str, Any] = {
            "openapi_url": str(app.openapi_url),
            "title": app.title + " - Swagger UI",
            "oauth2_redirect_url": app.swagger_ui_oauth2_redirect_url,
            "swagger_favicon_url": "/static/logo/trident_neptune_logo.ico",
        }

        if _settings.STATIC_DOCS:  # pragma: no branch
            kwargs.update(
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css",
            )

        return get_better_swagger_ui_html(**kwargs)

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        kwargs: dict[str, Any] = {
            "openapi_url": str(app.openapi_url),
            "title": app.title + " - ReDoc",
            "redoc_favicon_url": "/static/logo/trident_neptune_logo.ico",
        }

        if _settings.STATIC_DOCS:  # pragma: no branch
            kwargs.update(
                redoc_js_url="/static/redoc.standalone.js",
            )

        return get_redoc_html(**kwargs)

    @app.get("/config")
    async def check_config(context=Depends(get_valid_context)):
        return context

    @app.get("/ping")
    @app.get("/")
    async def ping():  # pragma: no cover
        logger.info("nereid engine ready.")
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.ALLOW_CORS_ORIGINS,
        allow_origin_regex=_settings.ALLOW_CORS_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS", "POST"],
        allow_headers=["*"],
    )

    app.add_middleware(BrotliMiddleware)

    return app
