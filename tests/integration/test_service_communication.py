# tests/integration/test_service_communication.py - Using environment configs
import pytest
import requests
import time
from pathlib import Path
import yaml


class TestServiceCommunication:
    """Integration tests for communication between services"""

    def load_test_config(self):
        """Load test configuration"""
        config_path = Path(__file__).parent.parent / "fixtures" / "test_configs.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def service_urls(self):
        """Get service URLs based on test environment"""
        config = self.load_test_config()

        # Determine environment (could be set via env var)
        import os

        env = os.getenv("TEST_ENV", "local")

        return config["test_environments"][env]

    def test_service_health_checks(self, service_urls):
        """Test that all services respond to health checks"""
        services = [
            ("robot-service", f"{service_urls['robot_service_url']}/robots"),
            ("log-api", f"{service_urls['log_api_url']}/logs"),
        ]

        for service_name, health_url in services:
            try:
                response = requests.get(health_url, timeout=5)
                assert (
                    response.status_code == 200
                ), f"{service_name} health check failed"
            except requests.exceptions.RequestException:
                pytest.skip(f"{service_name} not available for integration testing")

    def test_robot_service_to_log_api_flow(self, service_urls):
        """Test data flow from robot service to log API"""
        try:
            # Create a robot
            robot_data = {
                "id": "integration-robot",
                "name": "Integration Test Robot",
                "status": "online",
            }

            robot_response = requests.post(
                f"{service_urls['robot_service_url']}/robots",
                json=robot_data,
                timeout=5,
            )
            assert robot_response.status_code == 200

            # Wait for potential log processing
            time.sleep(2)

            # Check if logs were created
            log_response = requests.get(
                f"{service_urls['log_api_url']}/logs", timeout=5
            )
            assert log_response.status_code == 200

        except requests.exceptions.RequestException:
            pytest.skip("Services not available for integration testing")
