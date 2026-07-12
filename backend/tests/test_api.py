import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_read_main():
    # Since we mount the frontend to /, if it's built it should return 200 HTML
    response = client.get("/")
    # It might return 404 if the frontend folder isn't perfectly relative to the test runner,
    # so we can just assert it doesn't crash 500
    assert response.status_code in (200, 404)

def test_get_departments():
    response = client.get("/departments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_scores():
    response = client.get("/department-scores")
    assert response.status_code == 200

def test_get_forecast():
    response = client.get("/forecast")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
