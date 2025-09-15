# -*- coding: utf-8 -*-
# File: src/middleware/logging_middleware.py
# Logging middleware for FastAPI
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logger import LogManager

logger = LogManager.get_logger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            start = time.perf_counter()
            response = await call_next(request)

            duration = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                f"{request.method} {request.url.path} {response.status_code} [{duration}ms]"
            )
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)} ")
            raise e
