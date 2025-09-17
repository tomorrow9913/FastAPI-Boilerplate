# -*- coding: utf-8 -*-
# File: src/application/api/v1/service/sample/sample_route.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.api.dependencies import get_async_session
from src.application.api.v1.service.sample import sample_schema, sample_service

router = APIRouter(prefix="/sample", tags=["Sample"])


# 서비스 클래스를 의존성으로 주입받는 함수
def get_sample_service(
    db: AsyncSession = Depends(get_async_session),
) -> sample_service.SampleService:
    return sample_service.SampleService(db_session=db)


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.get("/error")
async def trigger_error():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="This is a sample error"
    )


@router.post(
    "/", response_model=sample_schema.Sample, status_code=status.HTTP_201_CREATED
)
async def create_sample_endpoint(
    sample_data: sample_schema.SampleCreate,
    sample_service: sample_service.SampleService = Depends(get_sample_service),
):
    try:
        # 라우트 핸들러는 단순히 서비스의 메서드를 호출하는 역할만 합니다.
        return await sample_service.create_new_sample(sample_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
