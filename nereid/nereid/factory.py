from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from nereid.api.api_v1.endpoints_sync import sync_router
from nereid.api.api_v1.utils import get_valid_context
from nereid.core.config import nereid_path, settings


def create_app(
    *,
    settings_override: Optional[Dict[str, Any]] = None,
    app_kwargs: Optional[Dict[str, Any]] = None
) -> FastAPI:

    _settings = settings.copy(deep=True)
    if settings_override is not None:  # pragma: no branch
        _settings.update(settings_override)

    kwargs = {}
    if app_kwargs is not None:  # pragma: no cover
        kwargs = app_kwargs

    _docs_url: Optional[str] = kwargs.pop("docs_url", None)
    _redoc_url: Optional[str] = kwargs.pop("redoc_url", None)

    app = FastAPI(
        title="nereid",
        version=_settings.VERSION,
        docs_url=_docs_url,
        redoc_url=_redoc_url,
        **kwargs
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.ALLOW_CORS_ORIGINS,
        allow_origin_regex=_settings.ALLOW_CORS_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS", "POST"],
        allow_headers=["*"],
    )

    if app.docs_url is None:  # pragma: no branch

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

    if app.redoc_url is None:  # pragma: no branch

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

    return app
