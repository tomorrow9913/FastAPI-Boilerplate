# -*- coding: utf-8 -*-
# File: tests/Integration/infrastructure/database/test_base_crud.py

import os
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.crud.base_crud import BaseRepository
from src.infrastructure.database.models import Base


# 테스트용 모델 정의
class TestUser(Base):
    __tablename__ = "test_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    age = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


# 테스트용 리포지토리
class TestUserRepository(BaseRepository[TestUser]):
    def __init__(self):
        super().__init__(TestUser)


# 테스트용 PostgreSQL 데이터베이스 URL 설정
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5432/test_database",
)
TEST_ASYNC_DATABASE_URL = os.getenv(
    "TEST_ASYNC_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@localhost:5432/test_database",
)


@pytest.fixture(scope="function")
def sync_db_session():
    """동기 SQLite 데이터베이스 세션 픽스처 (PostgreSQL 대신 SQLite 사용)"""
    # SQLite 메모리 데이터베이스 사용
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """비동기 SQLite 데이터베이스 세션 픽스처 (PostgreSQL 대신 SQLite 사용)"""
    # SQLite 비동기 연결
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def user_repository():
    """테스트 유저 리포지토리 픽스처"""
    return TestUserRepository()


@pytest.fixture
def sample_user_data():
    """샘플 유저 데이터 픽스처"""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "is_active": True,
    }


@pytest.fixture
def multiple_user_data():
    """여러 유저 데이터 픽스처"""
    return [
        {"name": "Alice", "email": "alice@example.com", "age": 25, "is_active": True},
        {"name": "Bob", "email": "bob@example.com", "age": 35, "is_active": False},
        {
            "name": "Charlie",
            "email": "charlie@example.com",
            "age": 28,
            "is_active": True,
        },
        {"name": "David", "email": "david@example.com", "age": 45, "is_active": True},
        {"name": "Eve", "email": "eve@example.com", "age": 32, "is_active": False},
    ]


class TestBaseRepositorySync:
    """동기 메서드 테스트 클래스"""

    def test_create_user(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """사용자 생성 테스트"""
        # When
        created_user = user_repository.create(sync_db_session, **sample_user_data)

        # Then
        assert created_user.id is not None
        assert created_user.name == sample_user_data["name"]
        assert created_user.email == sample_user_data["email"]
        assert created_user.age == sample_user_data["age"]
        assert created_user.is_active == sample_user_data["is_active"]
        assert created_user.created_at is not None
        assert created_user.updated_at is not None

    def test_get_by_pk(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """Primary Key로 조회 테스트"""
        # Given
        created_user = user_repository.create(sync_db_session, **sample_user_data)

        # When
        found_user = user_repository.get_by_pk(sync_db_session, created_user.id)

        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.name == created_user.name
        assert found_user.email == created_user.email

    def test_get_by_pk_not_found(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """존재하지 않는 Primary Key로 조회 테스트"""
        # When
        found_user = user_repository.get_by_pk(sync_db_session, 999)

        # Then
        assert found_user is None

    def test_get_one_with_filters(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """필터 조건으로 단일 객체 조회 테스트"""
        # Given
        created_user = user_repository.create(sync_db_session, **sample_user_data)

        # When
        found_user = user_repository.get_one(
            sync_db_session, email=sample_user_data["email"]
        )

        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]

    def test_get_one_not_found(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """필터 조건에 맞지 않는 객체 조회 테스트"""
        # When
        found_user = user_repository.get_one(
            sync_db_session, email="nonexistent@example.com"
        )

        # Then
        assert found_user is None

    def test_get_list_without_filters(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """필터 없이 전체 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(sync_db_session)

        # Then
        assert total_count == len(multiple_user_data)
        assert len(users) == len(multiple_user_data)

    def test_get_list_with_pagination(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """페이징이 적용된 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(sync_db_session, skip=1, limit=2)

        # Then
        assert total_count == len(multiple_user_data)
        assert len(users) == 2

    def test_get_list_with_filters(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """필터 조건이 적용된 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(sync_db_session, is_active=True)

        # Then
        active_users_count = sum(1 for user in multiple_user_data if user["is_active"])
        assert total_count == active_users_count
        assert len(users) == active_users_count
        assert all(user.is_active for user in users)

    def test_get_list_with_ordering_asc(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """오름차순 정렬 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(
            sync_db_session, order="asc", order_by="name"
        )

        # Then
        assert total_count == len(multiple_user_data)
        names = [user.name for user in users]
        assert names == sorted(names)

    def test_get_list_with_ordering_desc(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """내림차순 정렬 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(
            sync_db_session, order="desc", order_by="name"
        )

        # Then
        assert total_count == len(multiple_user_data)
        names = [user.name for user in users]
        assert names == sorted(names, reverse=True)

    def test_get_list_invalid_order(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """잘못된 정렬 순서 테스트"""
        # When & Then
        with pytest.raises(
            ValueError, match="Invalid order: invalid. Use 'asc' or 'desc'."
        ):
            user_repository.get_list(sync_db_session, order="invalid")

    def test_update_user(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """사용자 정보 수정 테스트"""
        # Given
        created_user = user_repository.create(sync_db_session, **sample_user_data)
        original_updated_at = created_user.updated_at
        update_data = {"name": "Jane Doe", "age": 31}

        # 시간차를 만들기 위해 잠깐 대기
        import time

        time.sleep(0.01)

        # When
        updated_user = user_repository.update(
            sync_db_session, created_user.id, **update_data
        )

        # Then
        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.name == update_data["name"]
        assert updated_user.age == update_data["age"]
        assert updated_user.email == sample_user_data["email"]  # 변경되지 않은 필드
        assert (
            updated_user.updated_at >= original_updated_at
        )  # 시간이 같거나 나중이어야 함

    def test_update_user_not_found(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """존재하지 않는 사용자 수정 테스트"""
        # When
        updated_user = user_repository.update(
            sync_db_session, 999, name="Non-existent User"
        )

        # Then
        assert updated_user is None

    def test_delete_user(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """사용자 삭제 테스트"""
        # Given
        created_user = user_repository.create(sync_db_session, **sample_user_data)

        # When
        result = user_repository.delete(sync_db_session, created_user.id)
        sync_db_session.commit()  # 트랜잭션 커밋

        # Then
        assert result is True
        deleted_user = user_repository.get_by_pk(sync_db_session, created_user.id)
        assert deleted_user is None

    def test_delete_user_not_found(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """존재하지 않는 사용자 삭제 테스트"""
        # When
        result = user_repository.delete(sync_db_session, 999)

        # Then
        assert result is False

    def test_soft_delete_user(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """사용자 소프트 삭제 테스트"""
        # Given
        created_user = user_repository.create(sync_db_session, **sample_user_data)

        # When
        result = user_repository.soft_delete(sync_db_session, created_user.id)
        sync_db_session.commit()  # 트랜잭션 커밋

        # Then
        assert result is True
        soft_deleted_user = user_repository.get_by_pk(sync_db_session, created_user.id)
        assert soft_deleted_user is not None
        assert soft_deleted_user.deleted_at is not None

    def test_soft_delete_user_not_found(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """존재하지 않는 사용자 소프트 삭제 테스트"""
        # When
        result = user_repository.soft_delete(sync_db_session, 999)

        # Then
        assert result is False


class TestBaseRepositoryAsync:
    """비동기 메서드 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_async_create_user(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 사용자 생성 테스트"""
        # When
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )

        # Then
        assert created_user.id is not None
        assert created_user.name == sample_user_data["name"]
        assert created_user.email == sample_user_data["email"]
        assert created_user.age == sample_user_data["age"]
        assert created_user.is_active == sample_user_data["is_active"]

    @pytest.mark.asyncio
    async def test_async_get_by_pk(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 Primary Key로 조회 테스트"""
        # Given
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )

        # When
        found_user = await user_repository.async_get_by_pk(
            async_db_session, created_user.id
        )

        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.name == created_user.name

    @pytest.mark.asyncio
    async def test_async_get_by_pk_not_found(
        self, async_db_session: AsyncSession, user_repository: TestUserRepository
    ):
        """비동기 존재하지 않는 Primary Key로 조회 테스트"""
        # When
        found_user = await user_repository.async_get_by_pk(async_db_session, 999)

        # Then
        assert found_user is None

    @pytest.mark.asyncio
    async def test_async_get_one_with_filters(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 필터 조건으로 단일 객체 조회 테스트"""
        # Given
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )

        # When
        found_user = await user_repository.async_get_one(
            async_db_session, email=sample_user_data["email"]
        )

        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_async_get_list_without_filters(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """비동기 필터 없이 전체 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            await user_repository.async_create(async_db_session, **user_data)

        # When
        total_count, users = await user_repository.async_get_list(async_db_session)

        # Then
        assert total_count == len(multiple_user_data)
        assert len(users) == len(multiple_user_data)

    @pytest.mark.asyncio
    async def test_async_get_list_with_pagination(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """비동기 페이징이 적용된 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            await user_repository.async_create(async_db_session, **user_data)

        # When
        total_count, users = await user_repository.async_get_list(
            async_db_session, skip=1, limit=2
        )

        # Then
        assert total_count == len(multiple_user_data)
        assert len(users) == 2

    @pytest.mark.asyncio
    async def test_async_get_list_with_filters(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """비동기 필터 조건이 적용된 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            await user_repository.async_create(async_db_session, **user_data)

        # When
        total_count, users = await user_repository.async_get_list(
            async_db_session, is_active=True
        )

        # Then
        active_users_count = sum(1 for user in multiple_user_data if user["is_active"])
        assert total_count == active_users_count
        assert len(users) == active_users_count
        assert all(user.is_active for user in users)

    @pytest.mark.asyncio
    async def test_async_get_list_invalid_order(
        self, async_db_session: AsyncSession, user_repository: TestUserRepository
    ):
        """비동기 잘못된 정렬 순서 테스트"""
        # When & Then
        with pytest.raises(
            ValueError, match="Invalid order: `invalid`. Use 'asc' or 'desc'."
        ):
            await user_repository.async_get_list(async_db_session, order="invalid")

    @pytest.mark.asyncio
    async def test_async_update_user(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 사용자 정보 수정 테스트"""
        # Given
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )
        original_updated_at = created_user.updated_at
        update_data = {"name": "Jane Doe", "age": 31}

        # 시간차를 만들기 위해 잠깐 대기
        import asyncio

        await asyncio.sleep(0.01)

        # When
        updated_user = await user_repository.async_update(
            async_db_session, created_user.id, **update_data
        )

        # Then
        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.name == update_data["name"]
        assert updated_user.age == update_data["age"]
        assert updated_user.email == sample_user_data["email"]
        assert (
            updated_user.updated_at >= original_updated_at
        )  # 시간이 같거나 나중이어야 함

    @pytest.mark.asyncio
    async def test_async_update_user_not_found(
        self, async_db_session: AsyncSession, user_repository: TestUserRepository
    ):
        """비동기 존재하지 않는 사용자 수정 테스트"""
        # When & Then
        with pytest.raises(
            ValueError, match="Object with primary key `999` not found in TestUser."
        ):
            await user_repository.async_update(
                async_db_session, 999, name="Non-existent User"
            )

    @pytest.mark.asyncio
    async def test_async_delete_user(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 사용자 삭제 테스트"""
        # Given
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )

        # When
        result = await user_repository.async_delete(async_db_session, created_user.id)

        # Then
        assert result is True
        deleted_user = await user_repository.async_get_by_pk(
            async_db_session, created_user.id
        )
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_async_delete_user_not_found(
        self, async_db_session: AsyncSession, user_repository: TestUserRepository
    ):
        """비동기 존재하지 않는 사용자 삭제 테스트"""
        # When
        result = await user_repository.async_delete(async_db_session, 999)

        # Then
        assert result is False

    @pytest.mark.asyncio
    async def test_async_soft_delete_user(
        self,
        async_db_session: AsyncSession,
        user_repository: TestUserRepository,
        sample_user_data: dict,
    ):
        """비동기 사용자 소프트 삭제 테스트"""
        # Given
        created_user = await user_repository.async_create(
            async_db_session, **sample_user_data
        )

        # When
        result = await user_repository.async_soft_delete(
            async_db_session, created_user.id
        )

        # Then
        assert result is True
        soft_deleted_user = await user_repository.async_get_by_pk(
            async_db_session, created_user.id
        )
        assert soft_deleted_user is not None
        assert soft_deleted_user.deleted_at is not None

    @pytest.mark.asyncio
    async def test_async_soft_delete_user_not_found(
        self, async_db_session: AsyncSession, user_repository: TestUserRepository
    ):
        """비동기 존재하지 않는 사용자 소프트 삭제 테스트"""
        # When
        result = await user_repository.async_soft_delete(async_db_session, 999)

        # Then
        assert result is False


class TestBaseRepositoryEdgeCases:
    """엣지 케이스 테스트 클래스"""

    def test_apply_filters_with_cast_filter(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """필터 캐스팅이 적용된 조회 테스트"""
        # Given
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "is_active": True,
        }
        created_user = user_repository.create(sync_db_session, **user_data)

        # When - 문자열로 필터 조건 전달 (model_cast에 의해 자동 캐스팅됨)
        found_user = user_repository.get_one(
            sync_db_session, age="25", is_active="true"
        )

        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.age == 25
        assert found_user.is_active is True

    def test_create_with_string_values_casting(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """문자열 값으로 생성 시 캐스팅 테스트"""
        # Given
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": "30",
            "is_active": "true",
        }

        # When
        created_user = user_repository.create(sync_db_session, **user_data)

        # Then
        assert created_user.age == 30
        assert created_user.is_active is True

    def test_get_list_empty_result(
        self, sync_db_session: Session, user_repository: TestUserRepository
    ):
        """빈 결과 목록 조회 테스트"""
        # When
        total_count, users = user_repository.get_list(sync_db_session)

        # Then
        assert total_count == 0
        assert len(users) == 0

    def test_get_list_with_zero_limit(
        self,
        sync_db_session: Session,
        user_repository: TestUserRepository,
        multiple_user_data: list,
    ):
        """limit이 0인 경우 목록 조회 테스트"""
        # Given
        for user_data in multiple_user_data:
            user_repository.create(sync_db_session, **user_data)

        # When
        total_count, users = user_repository.get_list(sync_db_session, limit=0)

        # Then
        assert total_count == len(multiple_user_data)
        assert len(users) == 0

    def test_primary_key_detection(self, user_repository: TestUserRepository):
        """Primary Key 자동 감지 테스트"""
        # Then
        assert user_repository._primary_key_name == "id"
