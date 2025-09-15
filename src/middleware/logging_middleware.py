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
        start = time.perf_counter()
        response = await call_next(request)

        duration = round((time.perf_counter() - start) * 1000, 2)

        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f'{client_ip} - "{request.method} {request.url.path}" {response.status_code} [{duration}ms]'
        )
        return response
