import pytest
import sys
import os
import yaml
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add each service's root directory (not subdirectories)
sys.path.insert(0, str(project_root / "robot-service"))
sys.path.insert(0, str(project_root / "log-api"))

def load_test_config():
    """Load test configuration from YAML file"""
    config_path = Path(__file__).parent / "fixtures" / "test_configs.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Return default config if file doesn't exist
        return {
            'test_data': {'sample_robot_count': 4},
            'performance_thresholds': {
                'response_time': {'p95': 500, 'p99': 1000},
                'throughput': {'min_rps': 100}
            },
            'security_tests': {
                'test_payloads': {
                    'sql_injection': ["'; DROP TABLE robots; --", "1' OR '1'='1"],
                    'xss': ["<script>alert('xss')</script>", "javascript:alert('xss')"],
                    'oversized_data': {
                        'robot_name_max_length': 10000,
                        'robot_id_max_length': 1000
                    }
                }
            }
        }

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration for all tests"""
    return load_test_config()

@pytest.fixture(scope="session")
def robot_service_client():
    """Provide a test client for robot-service"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"Could not import robot-service: {e}")

@pytest.fixture(scope="session") 
def log_api_client():
    """Provide a test client for log-api"""
    try:
        from fastapi.testclient import TestClient
        # We need to switch context for log-api
        import sys
        from pathlib import Path
        log_api_path = Path(__file__).parent.parent / "log-api"
        sys.path.insert(0, str(log_api_path))
        
        from app.main import app
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"Could not import log-api: {e}")

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