from locust import HttpUser, task, between
import random

class RobotServiceUser(HttpUser):
    """Locust performance test for Robot Service"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        self.robot_counter = 0
    
    @task(3)
    def get_robots(self):
        """Get all robots - most common operation"""
        self.client.get("/robots")
    
    @task(1)
    def create_robot(self):
        """Create a new robot"""
        self.robot_counter += 1
        robot_data = {
            "id": f"load-test-robot-{self.robot_counter}-{random.randint(1000, 9999)}",
            "name": f"Load Test Robot {self.robot_counter}",
            "status": random.choice(["online", "offline", "maintenance", "error"])
        }
        self.client.post("/robots", json=robot_data)
    
    @task(2)
    def get_metrics(self):
        """Get Prometheus metrics"""
        self.client.get("/metrics")
    
    @task(1)
    def update_robot(self):
        """Update an existing robot (might fail if robot doesn't exist)"""
        robot_id = f"load-test-robot-{random.randint(1, self.robot_counter)}-{random.randint(1000, 9999)}"
        update_data = {
            "status": random.choice(["online", "offline", "maintenance", "error"])
        }
        # Don't fail if robot doesn't exist
        with self.client.patch(f"/robot/{robot_id}", json=update_data, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()

class DashboardUser(HttpUser):
    """Locust performance test for Dashboard"""
    
    wait_time = between(2, 5)
    
    @task
    def load_dashboard(self):
        """Load the main dashboard page"""
        self.client.get("/")
    
    @task
    def load_static_assets(self):
        """Load static assets"""
        assets = ["/favicon.ico", "/static/css/main.css", "/static/js/main.js"]
        for asset in assets:
            with self.client.get(asset, catch_response=True) as response:
                if response.status_code in [200, 404]:  # 404 is ok for non-existent assets
                    response.success()