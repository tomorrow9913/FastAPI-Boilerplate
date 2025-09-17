from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import AppException, DuplicateError, NotFoundException
from src.core.logger import LogManager

logger = LogManager.get_logger("app")


def register_exception_handlers(app: FastAPI):
    """
    FastAPI 애플리케이션 인스턴스에 커스텀 예외 핸들러들을 등록합니다.
    이 함수는 server.py에서 호출됩니다.
    """

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        logger.warning(f"NotFoundError: {exc.detail} for request {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )

    @app.exception_handler(DuplicateError)
    async def duplicate_exception_handler(request: Request, exc: DuplicateError):
        logger.warning(f"DuplicateError: {exc.detail} for request {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.detail},
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.detail} for request {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """처리되지 않은 모든 예외를 잡아 로깅하고, 표준화된 JSON 응답을 반환합니다."""
        logger.exception(
            f"Unhandled exception occurred for request {request.url.path}: {exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )

    logger.info("Custom exception handlers registered.")
