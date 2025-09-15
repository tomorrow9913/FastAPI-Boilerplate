# -*- coding: utf-8 -*-
# File: src/middleware/yapppi_profile.py
# Yappi profiling middleware for FastAPI
import os
from contextvars import ContextVar

import yappi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import config

__LOAD__ = config.APP_CONFIG.YAPPI_PROFILE_ENABLE

ctx_id: ContextVar[int] = ContextVar("yappi_context")


def get_context_id() -> int:
    try:
        return ctx_id.get()
    except LookupError:
        return -1


yappi.set_tag_callback(get_context_id)


class YappiProfileMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> Response:
        ctx_id.set(id(request))
        with yappi.run():
            result = await call_next(request)

        stats = yappi.get_func_stats(tag=ctx_id.get())
        stats.sort(sort_type="ttot")
        stats.strip_dirs()
        if not stats.empty():
            if "YAPPI_PROFILE_CONSOLE" in os.environ:
                stats.print_all()
            stats.save("logs/yappi.prof", type="pstat")

        return result
