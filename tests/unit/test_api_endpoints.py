import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import time
import threading

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "robot-service"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "log-api"))

from robot_service.app.main import app as robot_app, robots_db

class TestRobotServiceIntegration:
    """Integration tests for Robot Service API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup for each test"""
        robots_db.clear()
        yield
        robots_db.clear()
    
    @pytest.fixture
    def client(self):
        return TestClient(robot_app)
    
    def test_full_robot_lifecycle(self, client):
        """Test complete robot lifecycle: create, read, update, delete flow"""
        robot_data = {
            "id": "lifecycle-robot",
            "name": "Lifecycle Test Robot",
            "status": "online"
        }
        
        # 1. Create robot
        create_response = client.post("/robots", json=robot_data)
        assert create_response.status_code == 200
        created_robot = create_response.json()
        assert created_robot == robot_data
        
        # 2. Verify robot appears in list
        list_response = client.get("/robots")
        assert list_response.status_code == 200
        robots_list = list_response.json()
        assert len(robots_list) == 1
        assert robots_list[0] == robot_data
        
        # 3. Update robot
        update_data = {"status": "maintenance", "name": "Updated Lifecycle Robot"}
        update_response = client.patch(f"/robot/{robot_data['id']}", json=update_data)
        assert update_response.status_code == 200
        updated_robot = update_response.json()
        assert updated_robot["status"] == "maintenance"
        assert updated_robot["name"] == "Updated Lifecycle Robot"
        assert updated_robot["id"] == robot_data["id"]
        
        # 4. Verify update persisted
        final_list_response = client.get("/robots")
        assert final_list_response.status_code == 200
        final_robots = final_list_response.json()
        assert len(final_robots) == 1
        assert final_robots[0]["status"] == "maintenance"
        assert final_robots[0]["name"] == "Updated Lifecycle Robot"
    
    def test_multiple_robots_management(self, client):
        """Test managing multiple robots simultaneously"""
        robots_data = [
            {"id": "multi-1", "name": "Multi Robot 1", "status": "online"},
            {"id": "multi-2", "name": "Multi Robot 2", "status": "offline"},
            {"id": "multi-3", "name": "Multi Robot 3", "status": "maintenance"},
            {"id": "multi-4", "name": "Multi Robot 4", "status": "error"}
        ]
        
        # Create all robots
        for robot_data in robots_data:
            response = client.post("/robots", json=robot_data)
            assert response.status_code == 200
        
        # Verify all robots exist
        list_response = client.get("/robots")
        assert list_response.status_code == 200
        robots_list = list_response.json()
        assert len(robots_list) == len(robots_data)
        
        # Verify each robot by ID
        created_ids = {robot["id"] for robot in robots_list}
        expected_ids = {robot["id"] for robot in robots_data}
        assert created_ids == expected_ids
        
        # Update each robot
        for i, robot_data in enumerate(robots_data):
            update_data = {"status": "updated", "name": f"Updated Robot {i+1}"}
            response = client.patch(f"/robot/{robot_data['id']}", json=update_data)
            assert response.status_code == 200
        
        # Verify all updates
        final_list_response = client.get("/robots")
        final_robots = final_list_response.json()
        assert all(robot["status"] == "updated" for robot in final_robots)
    
    def test_error_handling_flow(self, client):
        """Test error handling in various scenarios"""
        # Test creating robot with duplicate ID
        robot_data = {"id": "error-test", "name": "Error Test Robot", "status": "online"}
        
        # First creation should succeed
        response1 = client.post("/robots", json=robot_data)
        assert response1.status_code == 200
        
        # Second creation should fail
        response2 = client.post("/robots", json=robot_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
        
        # Test updating non-existent robot
        update_response = client.patch("/robot/non-existent", json={"status": "online"})
        assert update_response.status_code == 404
        assert "not found" in update_response.json()["detail"]
        
        # Test invalid data
        invalid_robot = {"name": "Invalid Robot"}  # Missing required fields
        invalid_response = client.post("/robots", json=invalid_robot)
        assert invalid_response.status_code == 422
    
    def test_metrics_integration(self, client):
        """Test metrics integration with robot operations"""
        initial_metrics = client.get("/metrics").text
        
        # Perform various operations
        robot_data = {"id": "metrics-test", "name": "Metrics Robot", "status": "online"}
        client.post("/robots", json=robot_data)
        client.get("/robots")
        client.patch("/robot/metrics-test", json={"status": "maintenance"})
        
        # Check that metrics changed
        final_metrics = client.get("/metrics").text
        assert final_metrics != initial_metrics
        
        # Verify specific metrics exist
        assert "robots_added_total" in final_metrics
        assert "request_duration_seconds" in final_metrics
        assert "robots_total" in final_metrics
    
    def test_concurrent_operations(self, client):
        """Test concurrent operations on the robot service"""
        results = {"created": [], "errors": []}
        
        def create_robot(robot_id):
            try:
                robot_data = {
                    "id": f"concurrent-{robot_id}",
                    "name": f"Concurrent Robot {robot_id}",
                    "status": "online"
                }
                response = client.post("/robots", json=robot_data)
                results["created"].append(response.status_code)
            except Exception as e:
                results["errors"].append(str(e))
        
        def update_robot(robot_id):
            try:
                update_data = {"status": "maintenance"}
                response = client.patch(f"/robot/concurrent-{robot_id}", json=update_data)
                # This might fail if robot doesn't exist yet, which is expected
                results["created"].append(response.status_code)
            except Exception as e:
                results["errors"].append(str(e))
        
        # Create multiple threads for robot creation
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_robot, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for creation threads
        for thread in threads:
            thread.join()
        
        # Brief pause to ensure all creations are complete
        time.sleep(0.1)
        
        # Verify results
        assert len(results["created"]) == 10
        assert all(status == 200 for status in results["created"])
        
        # Verify all robots were created
        list_response = client.get("/robots")
        assert list_response.status_code == 200
        robots_list = list_response.json()
        assert len(robots_list) == 10