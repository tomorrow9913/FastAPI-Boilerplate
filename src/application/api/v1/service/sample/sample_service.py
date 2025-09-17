# -*- coding: utf-8 -*-
# File: src/application/api/v1/service/sample/sample_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.api.v1.service.sample import sample_schema
from src.core.exceptions import DuplicateError
from src.core.logger import LogManager
from src.crud.sample_crud import sample_repository

logger = LogManager.get_logger("app")


class SampleService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = sample_repository

    async def create_new_sample(
        self, sample_data: sample_schema.SampleCreate
    ) -> sample_schema.Sample:
        # 여기에 복잡한 비즈니스 로직이 들어갈 수 있습니다.
        # 예: 중복 이름 검사, 특정 조건에 따른 데이터 가공 등
        existing_sample = await self.repository.async_get_one(
            self.db_session, name=sample_data.name
        )
        if existing_sample:
            # 주석: 아래 3번 항목에서 설명할 커스텀 예외 처리 방식
            raise DuplicateError("Sample with this name already exists.")

        # Repository를 통해 DB 작업 수행
        new_sample_model = await self.repository.async_create(
            self.db_session, **sample_data.model_dump()
        )

        # 스키마로 변환하여 반환
        return sample_schema.Sample.model_validate(new_sample_model)
