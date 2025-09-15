# Test Setup and Execution Guide

## 테스트 환경 설정

### 1. 테스트용 PostgreSQL 데이터베이스 설정

테스트를 실행하기 전에 PostgreSQL 테스트 데이터베이스를 설정해야 합니다.

```sql
-- PostgreSQL에서 테스트용 데이터베이스와 사용자 생성
CREATE USER test_user WITH PASSWORD 'test_password';
CREATE DATABASE test_database OWNER test_user;
GRANT ALL PRIVILEGES ON DATABASE test_database TO test_user;
```

### 2. 환경 변수 설정

`.env.test` 파일을 프로젝트 루트에 생성하거나 다음 환경 변수를 설정하세요:

```bash
TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_database
TEST_ASYNC_DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5432/test_database
```

### 3. 테스트 의존성 설치

```bash
pip install -r requirements-test.txt
```

## 테스트 실행

### 전체 테스트 실행
```bash
pytest
```

### 특정 테스트 파일 실행
```bash
pytest tests/Integration/infrastructure/database/test_base_crud.py
```

### 특정 테스트 클래스 실행
```bash
pytest tests/Integration/infrastructure/database/test_base_crud.py::TestBaseRepositorySync
```

### 특정 테스트 메서드 실행
```bash
pytest tests/Integration/infrastructure/database/test_base_crud.py::TestBaseRepositorySync::test_create_user
```

### 비동기 테스트만 실행
```bash
pytest tests/Integration/infrastructure/database/test_base_crud.py::TestBaseRepositoryAsync
```

### 커버리지와 함께 실행
```bash
pytest --cov=src --cov-report=html
```

### 상세 출력과 함께 실행
```bash
pytest -v -s
```

## 테스트 구조

### TestBaseRepositorySync
- 동기 메서드들에 대한 테스트
- `create`, `get_by_pk`, `get_one`, `get_list`, `update`, `delete`, `soft_delete`

### TestBaseRepositoryAsync
- 비동기 메서드들에 대한 테스트
- `async_create`, `async_get_by_pk`, `async_get_one`, `async_get_list`, `async_update`, `async_delete`, `async_soft_delete`

### TestBaseRepositoryEdgeCases
- 엣지 케이스 및 예외 상황 테스트
- 필터 캐스팅, 빈 결과, 잘못된 입력값 등

## 주의사항

1. **데이터베이스 연결 실패 시**: PostgreSQL 연결이 실패하면 자동으로 SQLite 메모리 데이터베이스로 폴백됩니다.

2. **테스트 격리**: 각 테스트 함수마다 새로운 데이터베이스 세션을 생성하고, 테스트 후 데이터를 정리합니다.

3. **트랜잭션 관리**: 테스트 중 발생하는 모든 변경사항은 테스트 종료 후 롤백됩니다.

## 트러블슈팅

### PostgreSQL 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
pg_ctl status

# PostgreSQL 서비스 시작
pg_ctl start
```

### 권한 오류
```sql
-- 테스트 사용자에게 필요한 권한 부여
GRANT CREATE ON DATABASE test_database TO test_user;
GRANT USAGE ON SCHEMA public TO test_user;
GRANT CREATE ON SCHEMA public TO test_user;
```
