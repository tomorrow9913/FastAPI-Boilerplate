# -*- coding: utf-8 -*-
# File: src/crud/base_crud.py
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.core.logger import LogManager
from src.infrastructure.database.models import Base
from src.utils.model_cast import cast_filter

logger = LogManager.get_logger("app")

# 이 리포지토리가 다룰 모델의 타입을 정의합니다.
ModelType = TypeVar("ModelType", bound=Base)


# --- 제네릭 리포지토리 클래스 ---
class BaseRepository(Generic[ModelType]):
    """
    모든 모델에 대한 공통적인 CRUD 로직을 제공하는 제네릭 리포지토리 클래스입니다.
    동기(Session)와 비동기(AsyncSession)를 모두 지원합니다.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """
        리포지토리를 초기화합니다.

        :param model: 이 리포지토리가 다룰 SQLAlchemy 모델 클래스
        """
        self.model = model
        # 모델의 Primary Key 컬럼을 동적으로 찾아 저장합니다.
        self._primary_key_name = inspect(model).primary_key[0].name

    # --- 내부 헬퍼 메서드 ---
    def _apply_filters(self, query, filters: Dict[str, Any]) -> Any:
        """
        필터 조건을 쿼리에 적용합니다.

        :param query: SQLAlchemy 쿼리 객체
        :param filters: 필터 조건 딕셔너리
        :return: 필터가 적용된 쿼리 객체
        """
        casted_filters = cast_filter(self.model, filters)
        for key, value in casted_filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        return query

    # --- 동기(Sync) 메서드 ---

    def get_by_pk(self, db: Session, pk: Any) -> Optional[ModelType]:
        """
        Primary Key로 단일 객체를 조회합니다.

        :param db: SQLAlchemy 세션 객체
        :param pk: Primary Key 값
        :return: 조회된 객체 또는 None
        """
        query = select(self.model).where(
            getattr(self.model, self._primary_key_name) == pk
        )
        return db.execute(query).scalar_one_or_none()

    def get_one(self, db: Session, **filters: Any) -> Optional[ModelType]:
        """
        필터 조건에 맞는 단일 객체를 조회합니다.

        :param db: SQLAlchemy 세션 객체
        :param filters: 필터 조건 딕셔너리
        :return: 조회된 객체 또는 None
        """
        query = self._apply_filters(select(self.model), filters)
        return db.execute(query).scalar_one_or_none()

    def get_list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order: str = "desc",
        order_by: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[int, List[ModelType]]:
        """
        페이징을 지원하는 객체 목록을 조회합니다.
        :param db: SQLAlchemy 세션 객체
        :param skip: 조회 시작 위치 (오프셋)
        :param limit: 조회할 최대 객체 수
        :param order: 정렬 순서 ("asc" 또는 "desc")
        :param order_by: 정렬할 컬럼 이름
        :param filters: 필터 조건 딕셔너리
        :return: 총 객체 수와 조회된 객체 목록의 튜플
        :raises ValueError: order가 "asc" 또는 "desc"가 아닐 경우
        """
        if order.lower() not in ["asc", "desc"]:
            raise ValueError(f"Invalid order: {order}. Use 'asc' or 'desc'.")

        base_query = self._apply_filters(select(self.model), filters)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_query).scalar() or 0

        order_by_column = getattr(self.model, order_by or self._primary_key_name)
        if order.lower() == "desc":
            base_query = base_query.order_by(order_by_column.desc())
        else:
            base_query = base_query.order_by(order_by_column.asc())

        items_query = base_query.offset(skip * limit).limit(limit)
        items = db.execute(items_query).scalars().all()

        return total_count, items

    def create(self, db: Session, **item_data: Any) -> ModelType:
        """
        새로운 객체를 생성합니다.
        """
        casted_data = cast_filter(self.model, item_data)
        db_obj = self.model(**casted_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, pk: Any, **update_data: Any) -> Optional[ModelType]:
        """
        기존 객체를 수정합니다.
        """
        db_obj = self.get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            return None

        casted_data = cast_filter(self.model, update_data)
        for key, value in casted_data.items():
            setattr(db_obj, key, value)

        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.now()

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, pk: Any) -> bool:
        """
        객체를 삭제합니다.
        트랜잭션 관리는 세션에 위임합니다.
        """
        db_obj = self.get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            return False
        db.delete(db_obj)
        # 커밋은 세션 트랜잭션 컨텍스트에 위임
        return True

    def soft_delete(self, db: Session, pk: Any) -> bool:
        """
        객체를 소프트 삭제합니다. (예: deleted_at 컬럼을 업데이트)
        트랜잭션 관리는 세션에 위임합니다.
        """
        db_obj = self.get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            return False

        if hasattr(db_obj, "deleted_at"):
            db_obj.deleted_at = datetime.now()
            # 커밋 및 refresh는 세션 트랜잭션 컨텍스트에 위임
            return True

        logger.warning(f"Model {self.model.__name__} does not support soft delete.")
        return False

    # --- 비동기(Async) 메서드 ---

    async def async_get_by_pk(self, db: AsyncSession, pk: Any) -> Optional[ModelType]:
        """
        Primary Key로 단일 객체를 비동기 조회합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param pk: Primary Key 값
        :return: 조회된 객체 또는 None
        """
        query = select(self.model).where(
            getattr(self.model, self._primary_key_name) == pk
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def async_get_one(
        self, db: AsyncSession, **filters: Any
    ) -> Optional[ModelType]:
        """
        필터 조건에 맞는 단일 객체를 비동기 조회합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param filters: 필터 조건 딕셔너리
        :return: 조회된 객체 또는 None
        """
        query = self._apply_filters(select(self.model), filters)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def async_get_list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order: str = "desc",
        order_by: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[int, List[ModelType]]:
        """
        페이징을 지원하는 객체 목록을 비동기 조회합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param skip: 조회 시작 위치 (오프셋)
        :param limit: 조회할 최대 객체 수
        :param order: 정렬 순서 ("asc" 또는 "desc")
        :param order_by: 정렬할 컬럼 이름
        :param filters: 필터 조건 딕셔너리
        :return: 총 객체 수와 조회된 객체 목록의 튜플
        :raises ValueError: order가 "asc" 또는 "desc"가 아닐 경우
        """
        if order.lower() not in ["asc", "desc"]:
            raise ValueError(f"Invalid order: `{order}`. Use 'asc' or 'desc'.")
        base_query = self._apply_filters(select(self.model), filters)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_res = await db.execute(count_query)
        total_count = total_count_res.scalar() or 0

        order_by_column = getattr(self.model, order_by or self._primary_key_name)
        if order.lower() == "desc":
            base_query = base_query.order_by(order_by_column.desc())
        else:
            base_query = base_query.order_by(order_by_column.asc())

        items_query = base_query.offset(skip * limit).limit(limit)
        items_res = await db.execute(items_query)
        items = items_res.scalars().all()

        return total_count, items

    async def async_create(self, db: AsyncSession, **item_data: Any) -> ModelType:
        """
        새로운 객체를 비동기 생성합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param item_data: 생성할 객체의 데이터 딕셔너리
        :return: 생성된 객체
        :raises ValueError: item_data에 필수 필드가 누락/타입이 맞지 않을 경우
        """
        casted_data = cast_filter(self.model, item_data)
        db_obj = self.model(**casted_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def async_update(
        self, db: AsyncSession, pk: Any, **update_data: Any
    ) -> Optional[ModelType]:
        """
        기존 객체를 비동기 수정합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param pk: 수정할 객체의 Primary Key 값
        :param update_data: 수정할 데이터 딕셔너리
        :return: 수정된 객체 또는 None
        :raises ValueError: update_data에 필수 필드가 누락/타입이 맞지 않을 경우
        """
        db_obj = await self.async_get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            raise ValueError(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )

        casted_data = cast_filter(self.model, update_data)
        for key, value in casted_data.items():
            setattr(db_obj, key, value)

        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def async_delete(self, db: AsyncSession, pk: Any) -> bool:
        """
        객체를 비동기 삭제합니다.

        :param db: SQLAlchemy 비동기 세션 객체
        :param pk: 삭제할 객체의 Primary Key 값
        :return: 삭제 성공 여부 (True/False)
        """
        db_obj = await self.async_get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    async def async_soft_delete(self, db: AsyncSession, pk: Any) -> bool:
        """
        객체를 비동기 소프트 삭제합니다. (예: deleted_at 컬럼을 업데이트)
        :param db: SQLAlchemy 비동기 세션 객체
        :param pk: 소프트 삭제할 객체의 Primary Key 값
        :return: 소프트 삭제 성공 여부 (True/False)
        """
        db_obj = await self.async_get_by_pk(db, pk)
        if not db_obj:
            logger.warning(
                f"Object with primary key `{pk}` not found in {self.model.__name__}."
            )
            return False

        if hasattr(db_obj, "deleted_at"):
            db_obj.deleted_at = datetime.now()
            await db.commit()
            await db.refresh(db_obj)
            return True

        logger.warning(f"Model `{self.model.__name__}` does not support soft delete.")
        return False
