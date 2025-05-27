import sys
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

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
        """Test basic health check"""
        response = client.get("/robots")
        assert response.status_code == 200

    def test_get_robots_empty(self, client):
        """Test getting robots when database is empty"""
        response = client.get("/robots")
        assert response.status_code == 200
        assert response.json() == []

    def test_add_robot_success(self, client, sample_robot):
        """Test successfully adding a new robot"""
        response = client.post("/robots", json=sample_robot)
        assert response.status_code == 200
        assert response.json() == sample_robot

    def test_security_sql_injection(self, client, security_payloads):
        """Test SQL injection protection using config payloads"""
        sql_payloads = security_payloads.get("sql_injection", [])

        for payload in sql_payloads:
            robot_data = {
                "id": "sql-test",
                "name": payload,  # Inject SQL payload in name field
                "status": "online",
            }
            response = client.post("/robots", json=robot_data)
            # Should either succeed (payload handled safely) or fail with validation error
            assert response.status_code in [200, 422, 400]

            # If successful, verify the payload was stored as-is (not executed)
            if response.status_code == 200:
                assert response.json()["name"] == payload

            # Clean up
            robots_db.clear()

    def test_security_xss_protection(self, client, security_payloads):
        """Test XSS protection using config payloads"""
        xss_payloads = security_payloads.get("xss", [])

        for payload in xss_payloads:
            robot_data = {
                "id": "xss-test",
                "name": payload,  # Inject XSS payload
                "status": "online",
            }
            response = client.post("/robots", json=robot_data)
            # Should handle XSS payloads safely
            assert response.status_code in [200, 422, 400]

            if response.status_code == 200:
                # Verify payload is stored as-is (not executed)
                assert response.json()["name"] == payload

            robots_db.clear()

    def test_oversized_data_protection(self, client, security_payloads):
        """Test oversized data protection using config limits"""
        oversized_config = security_payloads.get("oversized_data", {})
        max_name_length = oversized_config.get("robot_name_max_length", 10000)

        # Create oversized robot name
        oversized_name = "A" * max_name_length
        robot_data = {
            "id": "oversized-test",
            "name": oversized_name,
            "status": "online",
        }

        response = client.post("/robots", json=robot_data)
        # Should either handle gracefully or reject
        assert response.status_code in [200, 422, 400, 413]

    def test_performance_response_time(self, client, performance_thresholds):
        """Test response time meets performance thresholds"""
        import time

        p95_threshold = performance_thresholds.get("response_time", {}).get(
            "p95", 500
        )  # ms

        # Test multiple requests and measure response time
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.get("/robots")
            end_time = time.time()

            assert response.status_code == 200
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)

        # Check that 95% of requests are under threshold
        response_times.sort()
        p95_time = response_times[int(0.95 * len(response_times))]
        assert (
            p95_time < p95_threshold
        ), f"P95 response time {p95_time}ms exceeds threshold {p95_threshold}ms"
