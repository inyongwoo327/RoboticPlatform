"""
Utility module for loading test configurations.
This can be imported by any test file that needs access to configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_test_config() -> Dict[str, Any]:
    """
    Load test configuration from YAML file.

    Returns:
        Dict containing all test configuration
    """
    config_path = Path(__file__).parent.parent / "fixtures" / "test_configs.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Test config file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_service_urls(environment: str = "local") -> Dict[str, str]:
    """
    Get service URLs for a specific environment.

    Args:
        environment: Environment name ('local', 'docker', 'ci')

    Returns:
        Dict containing service URLs
    """
    config = load_test_config()
    return config["test_environments"][environment]


def get_performance_thresholds() -> Dict[str, Any]:
    """Get performance testing thresholds."""
    config = load_test_config()
    return config.get("performance_thresholds", {})


def get_security_payloads() -> Dict[str, Any]:
    """Get security test payloads."""
    config = load_test_config()
    return config.get("security_tests", {}).get("test_payloads", {})
