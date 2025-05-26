from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


# Please Clear the database before each test!!!
@pytest.fixture(autouse=True)
def clear_robots_db():
    from app.main import robots_db

    robots_db.clear()
    yield


def test_get_robots_empty():
    response = client.get("/robots")
    assert response.status_code == 200
    assert response.json() == []


def test_add_robot():
    robot = {"id": "r1", "name": "Robot1", "status": "active"}
    response = client.post("/robots", json=robot)
    assert response.status_code == 200
    assert response.json() == robot

    response = client.get("/robots")
    assert len(response.json()) == 1
    assert response.json()[0] == robot


def test_update_robot():
    robot = {"id": "r2", "name": "Robot2", "status": "active"}
    client.post("/robots", json=robot)

    update = {"status": "inactive"}
    response = client.patch(f"/robot/{robot['id']}", json=update)
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"
    assert response.json()["name"] == robot["name"]


def test_add_robot_duplicate_id():
    robot = {"id": "r1", "name": "Robot1", "status": "active"}
    client.post("/robots", json=robot)

    duplicate_robot = {"id": "r1", "name": "Another Robot", "status": "inactive"}
    response = client.post("/robots", json=duplicate_robot)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_nonexistent_robot():
    update = {"status": "inactive"}
    response = client.patch("/robot/nonexistent", json=update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_robot_name_only():
    robot = {"id": "r3", "name": "Robot3", "status": "active"}
    client.post("/robots", json=robot)

    update = {"name": "Updated Robot Name"}
    response = client.patch(f"/robot/{robot['id']}", json=update)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Robot Name"
    assert response.json()["status"] == robot["status"]


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert (
        response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    )

    robot = {"id": "test-metrics", "name": "Test Metrics", "status": "active"}
    client.post("/robots", json=robot)

    response = client.get("/metrics")
    assert "robots_added_total" in response.text
