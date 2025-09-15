# -*- coding: utf-8 -*-
# test/unit/utils/test_model_cast.py
from datetime import datetime

import pytest
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.types import TypeDecorator

from src.infrastructure.database.models import Base
from src.utils.model_cast import (
    _cast_to_bool,
    _cast_to_datetime,
    _cast_to_float,
    _cast_to_int,
    cast_filter,
)


# 테스트용 SQLAlchemy 모델 정의
class MockUser(Base):
    __tablename__ = "mock_users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_active = Column(Boolean)
    score = Column(Float)
    created_at = Column(DateTime)


# TypeDecorator 테스트용 커스텀 타입
class CustomStringType(TypeDecorator):
    impl = String
    cache_ok = True


class MockUserWithCustomType(Base):
    __tablename__ = "mock_users_custom"
    id = Column(Integer, primary_key=True)
    custom_field = Column(CustomStringType)


class TestCastingFunctions:
    """개별 캐스팅 함수들에 대한 테스트"""

    def test_cast_to_int_success(self):
        """정수 변환 성공 케이스"""
        assert _cast_to_int("123") == 123
        assert _cast_to_int("0") == 0
        assert _cast_to_int("-456") == -456

    def test_cast_to_int_failure(self):
        """정수 변환 실패 케이스"""
        with pytest.raises(ValueError):
            _cast_to_int("abc")
        with pytest.raises(ValueError):
            _cast_to_int("12.34")

    def test_cast_to_float_success(self):
        """실수 변환 성공 케이스"""
        assert _cast_to_float("123.45") == 123.45
        assert _cast_to_float("0.0") == 0.0
        assert _cast_to_float("-456.78") == -456.78
        assert _cast_to_float("123") == 123.0

    def test_cast_to_float_failure(self):
        """실수 변환 실패 케이스"""
        with pytest.raises(ValueError):
            _cast_to_float("abc")

    def test_cast_to_bool_true_values(self):
        """불리언 True 값 변환 테스트"""
        true_values = ["true", "1", "yes", "y", "t", "TRUE", "Yes", "T"]
        for value in true_values:
            assert _cast_to_bool(value) is True

    def test_cast_to_bool_false_values(self):
        """불리언 False 값 변환 테스트"""
        false_values = ["false", "0", "no", "n", "f", "FALSE", "No", "F"]
        for value in false_values:
            assert _cast_to_bool(value) is False

    def test_cast_to_bool_invalid_value(self):
        """불리언 변환 실패 케이스"""
        with pytest.raises(ValueError, match="Cannot convert to boolean"):
            _cast_to_bool("maybe")

    def test_cast_to_datetime_success(self):
        """날짜시간 변환 성공 케이스"""
        # 전체 datetime 형식
        result = _cast_to_datetime("2023-12-25 14:30:00")
        expected = datetime(2023, 12, 25, 14, 30, 0)
        assert result == expected

        # 날짜만 형식
        result = _cast_to_datetime("2023-12-25")
        expected = datetime(2023, 12, 25, 0, 0, 0)
        assert result == expected

    def test_cast_to_datetime_failure(self):
        """날짜시간 변환 실패 케이스"""
        with pytest.raises(ValueError, match="Cannot convert .* to datetime"):
            _cast_to_datetime("invalid-date")
        with pytest.raises(ValueError, match="Cannot convert .* to datetime"):
            _cast_to_datetime("2023/12/25")  # 잘못된 형식


class TestCastFilter:
    """cast_filter 함수에 대한 포괄적 테스트"""

    def test_cast_filter_all_types_success(self):
        """모든 데이터 타입에 대한 성공적인 형변환 테스트"""
        filters = {
            "id": "123",
            "name": "test_user",
            "is_active": "true",
            "score": "85.5",
            "created_at": "2023-12-25 14:30:00",
        }
        casted = cast_filter(MockUser, filters)

        assert casted["id"] == 123
        assert casted["name"] == "test_user"
        assert casted["is_active"] is True
        assert casted["score"] == 85.5
        assert casted["created_at"] == datetime(2023, 12, 25, 14, 30, 0)

    def test_cast_filter_with_non_string_values(self):
        """문자열이 아닌 값들은 그대로 유지되는지 테스트"""
        filters = {
            "id": 123,  # 이미 정수
            "is_active": True,  # 이미 불리언
            "score": 85.5,  # 이미 실수
            "name": "test_user",  # 문자열
        }
        casted = cast_filter(MockUser, filters)

        assert casted["id"] == 123
        assert casted["is_active"] is True
        assert casted["score"] == 85.5
        assert casted["name"] == "test_user"

    def test_cast_filter_with_null_values(self):
        """null/none 값 처리 테스트"""
        filters = {
            "name": "null",
            "is_active": "none",
            "score": "NULL",
            "created_at": "None",
        }
        casted = cast_filter(MockUser, filters)

        assert casted["name"] is None
        assert casted["is_active"] is None
        assert casted["score"] is None
        assert casted["created_at"] is None

    def test_cast_filter_with_empty_filters(self):
        """빈 필터 딕셔너리 처리 테스트"""
        filters = {}
        casted = cast_filter(MockUser, filters)
        assert casted == {}

    def test_cast_filter_with_invalid_integer(self):
        """잘못된 정수 값에 대한 ValueError 테스트"""
        filters = {"id": "not-a-number"}
        with pytest.raises(ValueError, match="Invalid value for 'id'"):
            cast_filter(MockUser, filters)

    def test_cast_filter_with_invalid_float(self):
        """잘못된 실수 값에 대한 ValueError 테스트"""
        filters = {"score": "not-a-float"}
        with pytest.raises(ValueError, match="Invalid value for 'score'"):
            cast_filter(MockUser, filters)

    def test_cast_filter_with_invalid_boolean(self):
        """잘못된 불리언 값에 대한 ValueError 테스트"""
        filters = {"is_active": "maybe"}
        with pytest.raises(ValueError, match="Invalid value for 'is_active'"):
            cast_filter(MockUser, filters)

    def test_cast_filter_with_invalid_datetime(self):
        """잘못된 날짜시간 값에 대한 ValueError 테스트"""
        filters = {"created_at": "invalid-date"}
        with pytest.raises(ValueError, match="Invalid value for 'created_at'"):
            cast_filter(MockUser, filters)

    def test_cast_filter_with_invalid_key(self):
        """존재하지 않는 컬럼 키에 대한 AttributeError 테스트"""
        filters = {"non_existent_key": "some_value"}
        with pytest.raises(
            AttributeError, match="Filter key 'non_existent_key' does not exist"
        ):
            cast_filter(MockUser, filters)

    def test_cast_filter_with_type_decorator(self):
        """TypeDecorator를 사용하는 컬럼 처리 테스트"""
        filters = {"custom_field": "test_value"}
        casted = cast_filter(MockUserWithCustomType, filters)
        assert casted["custom_field"] == "test_value"

    def test_cast_filter_partial_success(self):
        """일부 필드만 있는 경우 테스트"""
        filters = {"id": "456", "name": "partial_user"}
        casted = cast_filter(MockUser, filters)

        assert casted["id"] == 456
        assert casted["name"] == "partial_user"
        assert len(casted) == 2

    def test_cast_filter_boolean_edge_cases(self):
        """불리언 변환의 다양한 케이스 테스트"""
        test_cases = [
            ("1", True),
            ("0", False),
            ("YES", True),
            ("NO", False),
            ("T", True),
            ("F", False),
        ]

        for input_value, expected in test_cases:
            filters = {"is_active": input_value}
            casted = cast_filter(MockUser, filters)
            assert casted["is_active"] is expected

    def test_cast_filter_preserves_original_dict(self):
        """원본 딕셔너리가 변경되지 않는지 테스트"""
        original_filters = {"id": "123", "name": "test_user", "is_active": "true"}
        filters_copy = original_filters.copy()

        cast_filter(MockUser, original_filters)

        # 원본 딕셔너리가 변경되지 않았는지 확인
        assert original_filters == filters_copy
