from locust import HttpUser, task, between
import random
import yaml
from pathlib import Path


def load_test_config():
    """Load test configuration for performance tests"""
    config_path = Path(__file__).parent.parent / "fixtures" / "test_configs.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Load configuration
test_config = load_test_config()
load_config = test_config.get("load_testing", {})


class RobotServiceUser(HttpUser):
    """Locust performance test for Robot Service using config"""

    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts"""
        self.robot_counter = 0
        self.config = load_test_config()

    @task(3)
    def get_robots(self):
        """Get all robots - most common operation"""
        response = self.client.get("/robots")

        # Check performance threshold
        thresholds = self.config.get("performance_thresholds", {})
        p95_threshold = thresholds.get("response_time", {}).get("p95", 500)

        if response.elapsed.total_seconds() * 1000 > p95_threshold:
            print(
                f"Warning: Response time {response.elapsed.total_seconds() * 1000}ms exceeds P95 threshold"
            )

    @task(1)
    def create_robot(self):
        """Create a new robot"""
        self.robot_counter += 1
        robot_data = {
            "id": f"load-test-robot-{self.robot_counter}-{random.randint(1000, 9999)}",
            "name": f"Load Test Robot {self.robot_counter}",
            "status": random.choice(["online", "offline", "maintenance", "error"]),
        }
        self.client.post("/robots", json=robot_data)
