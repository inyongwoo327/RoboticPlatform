import pytest
import sys
import os
import yaml
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "robot-service"))
sys.path.insert(0, str(project_root / "log-api"))

from fastapi.testclient import TestClient

def load_test_config():
    """Load test configuration from YAML file"""
    config_path = Path(__file__).parent / "fixtures" / "test_configs.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration for all tests"""
    return load_test_config()

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
def sample_robots(test_config):
    """Provide multiple sample robots for testing"""
    # Use config to determine how many test robots to create
    robot_count = test_config.get('test_data', {}).get('sample_robot_count', 4)
    
    return [
        {"id": f"robot-{i+1}", "name": f"Robot {i+1}", "status": status}
        for i, status in enumerate(["online", "offline", "maintenance", "error"][:robot_count])
    ]

@pytest.fixture
def performance_thresholds(test_config):
    """Provide performance thresholds from config"""
    return test_config.get('performance_thresholds', {})

@pytest.fixture
def security_payloads(test_config):
    """Provide security test payloads from config"""
    return test_config.get('security_tests', {}).get('test_payloads', {})
