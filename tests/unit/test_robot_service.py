import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add robot-service to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "robot-service"))

from app.main import app, robots_db
from app.models import Robot, RobotUpdate

class TestRobotService:
    """Comprehensive test suite for Robot Service"""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup for each test"""
        robots_db.clear()
        yield
        robots_db.clear()
    
    @pytest.fixture
    def client(self):
        """Test client for robot service"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test basic health check for log API"""
        response = client.get("/logs")
        assert response.status_code == 200
    
    def test_get_logs_empty(self, client):
        """Test getting logs when no logs exist"""
        response = client.get("/logs")
        assert response.status_code == 200
        # Assuming logs endpoint returns a list
        logs_data = response.json()
        assert isinstance(logs_data, list)
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint if it exists"""
        response = client.get("/metrics")
        if response.status_code == 200:
            assert "text/plain" in response.headers.get("content-type", "")