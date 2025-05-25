import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import from both services
sys.path.insert(0, str(project_root / "robot-service"))
sys.path.insert(0, str(project_root / "log-api"))

from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def robot_service_client():
    """Provide a test client for robot-service"""
    from robot_service.app.main import app
    return TestClient(app)

@pytest.fixture(scope="session") 
def log_api_client():
    """Provide a test client for log-api"""
    from log_api.app.main import app
    return TestClient(app)

@pytest.fixture
def sample_robot():
    """Provide a sample robot for testing"""
    return {
        "id": "test-robot-001",
        "name": "Test Robot",
        "status": "online"
    }

@pytest.fixture
def sample_robots():
    """Provide multiple sample robots for testing"""
    return [
        {"id": "robot-1", "name": "Robot 1", "status": "online"},
        {"id": "robot-2", "name": "Robot 2", "status": "offline"},
        {"id": "robot-3", "name": "Robot 3", "status": "maintenance"},
        {"id": "robot-4", "name": "Robot 4", "status": "error"}
    ]

@pytest.fixture
def cleanup_robots(robot_service_client):
    """Clean up robots database after each test"""
    yield
    # Clear the robots database after test
    try:
        # Assuming there's a way to clear the database
        from robot_service.app.main import robots_db
        robots_db.clear()
    except ImportError:
        pass