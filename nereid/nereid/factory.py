import logging
from typing import Any, Dict, Optional

from brotli_asgi import BrotliMiddleware
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from nereid._compat import model_copy
from nereid.api.api_v1.endpoints_sync import sync_router
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.config import nereid_path, settings

logging.basicConfig(level=settings.LOGLEVEL)
logger = logging.getLogger(__name__)

timing_asgi = None
if settings.ASGI_TIMING:
    try:
        import timing_asgi
        from timing_asgi import TimingClient, TimingMiddleware
        from timing_asgi.integrations import StarletteScopeToName

        class PrintTimings(TimingClient):
            def timing(self, metric_name, timing, tags):
                print(metric_name, timing, tags)

    except ImportError:
        logger.warn("`timing-asgi` not installed. Use `pip install timing-asgi`.")


def create_app(
    *,
    settings_override: Optional[Dict[str, Any]] = None,
    app_kwargs: Optional[Dict[str, Any]] = None,
) -> FastAPI:
    _settings = model_copy(settings, deep=True)
    _settings.update(settings_override or {})

    kwargs = app_kwargs or {}

    if _settings.STATIC_DOCS:
        kwargs["docs_url"] = None
        kwargs["redoc_url"] = None

    app = FastAPI(
        title="nereid",
        version=_settings.VERSION,
        **kwargs,
    )
    app._settings = _settings  # type: ignore

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

    if _settings.STATIC_DOCS:  # pragma: no branch

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

    @app.get("/config")
    async def check_config(context=Depends(get_valid_context)):
        return context

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.ALLOW_CORS_ORIGINS,
        allow_origin_regex=_settings.ALLOW_CORS_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS", "POST"],
        allow_headers=["*"],
    )

    app.add_middleware(BrotliMiddleware)

    if timing_asgi is not None:
        app.add_middleware(
            TimingMiddleware,
            client=PrintTimings(),
            metric_namer=StarletteScopeToName(prefix="nereid", starlette_app=app),
        )

    return app
