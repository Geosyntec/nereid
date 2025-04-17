import logging
from typing import Any

from brotli_asgi import BrotliMiddleware
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from nereid.api import sync_router
from nereid.api.docs import get_better_swagger_ui_html
from nereid.api.utils import get_valid_context
from nereid.core import io
from nereid.core.config import nereid_path, settings
from nereid.models.response_models import JSONAPIResponse
from nereid.src.nomograph import nomo

logger = logging.getLogger(__name__)


def cache_clear():
    for func in [io._load_file, io._load_table, nomo.build_nomo]:
        func.cache_clear()


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
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    if _settings.ASYNC_MODE == "replace":  # pragma: no cover
        from nereid.api import async_router

        app.include_router(async_router, tags=["async"])
    else:
        app.include_router(sync_router)
        if _settings.ASYNC_MODE == "add":  # pragma: no cover
            from nereid.api import async_router

            app.include_router(
                async_router,
                prefix=_settings.ASYNC_ROUTE_PREFIX,
                tags=["async"],
            )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + str(app.openapi_url)
        kwargs: dict[str, Any] = {
            "openapi_url": openapi_url,
            "title": app.title + " - Swagger UI",
            "oauth2_redirect_url": root_path + str(app.swagger_ui_oauth2_redirect_url),
            "swagger_favicon_url": root_path + "/static/logo/trident_neptune_logo.ico",
        }

        if _settings.STATIC_DOCS:  # pragma: no branch
            kwargs.update(
                swagger_js_url=root_path + "/static/swagger-ui-bundle.js",
                swagger_css_url=root_path + "/static/swagger-ui.css",
            )

        return get_better_swagger_ui_html(**kwargs)

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + str(app.openapi_url)
        kwargs: dict[str, Any] = {
            "openapi_url": openapi_url,
            "title": app.title + " - ReDoc",
            "redoc_favicon_url": root_path + "/static/logo/trident_neptune_logo.ico",
        }

        if _settings.STATIC_DOCS:  # pragma: no branch
            kwargs.update(
                redoc_js_url=root_path + "/static/redoc.standalone.js",
            )

        return get_redoc_html(**kwargs)

    @app.get("/config")
    async def check_config(context=Depends(get_valid_context)):
        return context

    @app.get("/clear_cache")
    async def clear_cache():
        cache_clear()
        app._context_cache = {}  # type: ignore
        logger.info("configuration context cache cleared.")
        return RedirectResponse(app.url_path_for("check_config"))

    app.mount(
        "/app",
        StaticFiles(directory=static_path / "frontend/dist", html=True),
        name="app",
    )

    @app.get("/ping")
    @app.get("/")
    async def ping():  # pragma: no cover
        logger.info("nereid engine ready.")
        return JSONAPIResponse(**{"status": "ok", "data": "pong"})

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
