# src/application/api/v1/__init__.py

from fastapi import APIRouter

from src.application.api.v1.service import routers

router = APIRouter()

for route in routers:
    router.include_router(route)

__all__ = ["router"]
