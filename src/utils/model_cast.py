# -*- coding: utf-8 -*-
# File: src/utils/model_cast.py
from datetime import datetime
from typing import Any, Callable, Dict, Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.types import Boolean, DateTime, Float, Integer, String, TypeDecorator

from src.core.logger import LogManager
from src.infrastructure.database.models import Base

logger = LogManager.get_logger("app")
ModelType = TypeVar("ModelType", bound=Base)


def _cast_to_int(value: str) -> int:
    """문자열을 정수형으로 변환합니다."""
    return int(value)


def _cast_to_float(value: str) -> float:
    """문자열을 실수형으로 변환합니다."""
    return float(value)


def _cast_to_bool(value: str) -> bool:
    """문자열을 불리언 타입으로 변환합니다."""
    _TRUE_VALUES = {"true", "1", "yes", "y", "t"}
    _FALSE_VALUES = {"false", "0", "no", "n", "f"}
    val_str = value.lower()
    if val_str in _TRUE_VALUES:
        return True
    if val_str in _FALSE_VALUES:
        return False
    raise ValueError(f"Cannot convert to boolean: {value}")


def _cast_to_datetime(value: str) -> datetime:
    """문자열을 datetime 객체로 변환합니다."""
    _DATETIME_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot convert '{value}' to datetime. Use one of formats: {_DATETIME_FORMATS}"
    )


CASTING_MAP: Dict[Type, Callable[[str], Any]] = {
    Integer: _cast_to_int,
    Float: _cast_to_float,
    Boolean: _cast_to_bool,
    DateTime: _cast_to_datetime,
    String: str,
}


def cast_filter(model: Type[ModelType], filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    SQLAlchemy 모델의 컬럼 타입을 참조하여 필터 딕셔너리의 값들을 자동으로 형변환합니다.
    이 함수는 외부(API 등)로부터 받은 문자열 기반의 필터 값을 실제 쿼리에 사용하기 전에
    안전한 데이터 타입으로 변환하는 데 사용됩니다.

    :param model: SQLAlchemy 모델 클래스 (예: models.Nodes)
    :param filters: 변환할 필터 딕셔너리 (예: {"id": "123", "is_active": "true"})
    :return: 값이 형변환된 새로운 딕셔너리 (예: {"id": 123, "is_active": True})
    :raises AttributeError: 필터 키가 모델에 존재하지 않는 컬럼일 경우 발생
    :raises ValueError: 값을 해당 컬럼 타입으로 변환할 수 없는 경우 발생
    """
    mapper = inspect(model)
    column_type_map = {c.name: c.type for c in mapper.columns}
    casted_filters = {}

    for key, value in filters.items():
        if key not in column_type_map:
            raise AttributeError(
                f"Filter key '{key}' does not exist in model '{model.__name__}'."
            )

        if not isinstance(value, str):
            casted_filters[key] = value
            continue

        if value.lower() in ["null", "none"]:
            casted_filters[key] = None
            continue

        col_type = column_type_map[key]
        type_class = (
            col_type.impl.__class__
            if isinstance(col_type, TypeDecorator)
            else col_type.__class__
        )
        caster = CASTING_MAP.get(type_class)

        if not caster:
            casted_filters[key] = value
            logger.warning(
                f"No casting function found for type '{type_class.__name__}' for key '{key}'. Using raw value."
            )
            continue

        try:
            casted_filters[key] = caster(value)
        except (ValueError, TypeError) as e:
            logger.warning(
                "Failed to cast value for key '%s'. Value: '%s', Type: %s. Error: %s",
                key,
                value,
                type_class.__name__,
                e,
            )
            raise ValueError(f"Invalid value for '{key}'. Please check the format.")

    return casted_filters
