from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_api_title():
    assert app.title == "MatrixMeds API"

def test_api_version():
    assert app.version == "1.0.0"

def test_cors_middleware():
    # Test CORS headers
    response = client.options(
        "/health",
        headers={"Origin": settings.CORS_ORIGINS[0]}
    )
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == settings.CORS_ORIGINS[0]

def test_cors_middleware_invalid_origin():
    # Test CORS headers with invalid origin
    response = client.options(
        "/health",
        headers={"Origin": "http://invalid-origin.com"}
    )
    assert response.headers["access-control-allow-origin"] == "*" 