# -*- coding: utf-8 -*-
# src/server.py
# FastAPI application setup with dynamic sub-application mounting, middleware, and error handling

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import config
from src.core.logger import LogManager

logger = LogManager.get_logger("app")


def get_sub_applications_mount() -> dict[str, APIRouter]:
    """
    Returns a dictionary of sub-applications to be mounted on the main FastAPI app.
    The keys are the mount paths, and the values are the FastAPI applications.
    """
    import importlib
    import os
    import pathlib

    logger.info("Sub-applications 마운트를 시작합니다.")

    sub_api_app = {}

    api_dir = pathlib.Path(__file__).parent / "application" / "api"

    for folder_name in os.listdir(api_dir):
        sub_api_path = api_dir / folder_name

        # check if the path is a directory
        if sub_api_path.is_dir():
            sub_api_file = sub_api_path / "__init__.py"

            logger.debug(f"Checking sub-application: {sub_api_file}")

            if sub_api_file.is_file():
                # import the sub_api module
                module_name = f"src.application.api.{folder_name}"
                module = importlib.import_module(module_name)

                if hasattr(module, "router") and not getattr(
                    module, "__EXCLUDING_ROUTE__", False
                ):
                    sub_api_app[folder_name] = module.router
                    logger.info(f"Load Sub-application '{folder_name}'.")

    return sub_api_app


def init_sub_applications_mount(
    app_: FastAPI, app_dict: dict[str, APIRouter] | None = None
) -> None:
    if app_dict is None:
        raise ValueError("app_dict must be provided to mount sub-applications.")

    for mount_path, sub_router in app_dict.items():
        if not isinstance(sub_router, APIRouter):
            logger.error(
                f"Expected APIRouter instance for mount path: {mount_path}, got: {type(sub_router)}"
            )
            raise TypeError(
                f"Expected APIRouter instance for {mount_path}, got {type(sub_router)}"
            )

        # mount the sub_api to the main app
        if mount_path.startswith("/"):
            mount_path = mount_path[1:]

        # If you want absolute isolation, you can change it to a sub-api mount format.
        # In this case, you need to replace "src/application/api/{version}/__init__.py" from APIRouter to FastAPI.
        # https://fastapi.tiangolo.com/advanced/sub-applications/#top-level-application
        app_.include_router(sub_router, prefix=f"/{mount_path}")
        logger.info(f"Include '{mount_path}' router to the main application.")


def make_middleware() -> list[Middleware]:
    # Using src/middleware/__init__.py Loaded middlewares
    from src.middleware import middlewares

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    # Add automatically loaded middleware
    for mw in middlewares:
        logger.debug(f"Adding middleware: {mw.__name__}")
        middleware.append(Middleware(mw))

    return middleware


def create_app() -> FastAPI:
    sub_api = get_sub_applications_mount()

    app_ = FastAPI(
        title=config.APP_CONFIG.APP_NAME,
        description=config.APP_CONFIG.APP_DESCRIPTION,
        version=config.APP_CONFIG.APP_VERSION,
        docs_url=None if config.ENV == "prod" else "/docs",
        redoc_url=None if config.ENV == "prod" else "/redoc",
        openapi_url=None if config.ENV == "prod" else "/openapi.json",
        root_path="/api",
        middleware=make_middleware(),
    )

    logger.info("Create FastAPI application instance.")
    init_sub_applications_mount(app_, sub_api)

    return app_


app = create_app()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    처리되지 않은 모든 예외를 잡아 로깅하고, 표준화된 JSON 응답을 반환합니다.
    """
    logger.exception(f"처리되지 않은 예외 발생: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/health")
async def healthcheck(request: Request) -> dict:
    return {"status": "OK"}
