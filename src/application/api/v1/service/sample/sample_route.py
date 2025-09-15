# -*- coding: utf-8 -*-
# File: src/application/api/v1/service/sample/sample_route.py

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/sample", tags=["Sample"])


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.get("/error")
async def trigger_error():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="This is a sample error"
    )
