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