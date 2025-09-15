from fastapi.testclient import TestClient

from src.server import app

# TestClient 인스턴스 생성
client = TestClient(app)


def test_ping_endpoint():
    """GET /sample/ping 엔드포인트가 정상 동작하는지 테스트합니다."""
    response = client.get("/api/v1/sample/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_trigger_error_endpoint():
    """GET /sample/error 엔드포인트가 의도된 에러를 발생시키는지 테스트합니다."""
    response = client.get("/api/v1/sample/error")
    assert response.status_code == 400
    assert response.json() == {"detail": "This is a sample error"}
