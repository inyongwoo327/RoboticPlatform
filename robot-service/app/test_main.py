from fastapi.testclient import TestClient
from robot_service.app.main import app

client = TestClient(app)

def test_get_robots_empty():
    response = client.get("/robots")
    assert response.status_code == 200
    assert response.json() == []

def test_add_robot():
    robot = {"id": "r1", "name": "Robot1", "status": "active"}
    response = client.post("/robots", json=robot)
    assert response.status_code == 200
    assert response.json() == robot

def test_update_robot():
    robot = {"id": "r2", "name": "Robot2", "status": "active"}
    client.post("/robots", json=robot)
    update = {"status": "inactive"}
    response = client.patch("/robot/r2", json=update)
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"