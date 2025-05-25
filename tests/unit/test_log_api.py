import pytest
from pydantic import ValidationError
import sys
from pathlib import Path

# Add both services to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "robot-service"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "log-api"))

from robot_service.app.models import Robot, RobotUpdate

class TestRobotModel:
    """Test suite for Robot model validation"""
    
    def test_valid_robot_creation(self):
        """Test creating a valid robot"""
        robot = Robot(id="test-1", name="Test Robot", status="online")
        assert robot.id == "test-1"
        assert robot.name == "Test Robot"
        assert robot.status == "online"
    
    def test_robot_missing_required_fields(self):
        """Test robot creation with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            Robot(name="Test Robot", status="online")  # Missing id
        assert "id" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Robot(id="test-1", status="online")  # Missing name
        assert "name" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Robot(id="test-1", name="Test Robot")  # Missing status
        assert "status" in str(exc_info.value)
    
    def test_robot_empty_string_validation(self):
        """Test robot with empty string fields"""
        with pytest.raises(ValidationError):
            Robot(id="", name="Test Robot", status="online")
        
        with pytest.raises(ValidationError):
            Robot(id="test-1", name="", status="online")
        
        with pytest.raises(ValidationError):
            Robot(id="test-1", name="Test Robot", status="")
    
    def test_robot_field_types(self):
        """Test robot field type validation"""
        # All fields should be strings
        with pytest.raises(ValidationError):
            Robot(id=123, name="Test Robot", status="online")
        
        with pytest.raises(ValidationError):
            Robot(id="test-1", name=123, status="online")
        
        with pytest.raises(ValidationError):
            Robot(id="test-1", name="Test Robot", status=123)
    
    def test_robot_status_values(self):
        """Test different robot status values"""
        valid_statuses = ["online", "offline", "maintenance", "error", "unknown"]
        
        for status in valid_statuses:
            robot = Robot(id="test-1", name="Test Robot", status=status)
            assert robot.status == status
    
    def test_robot_json_serialization(self):
        """Test robot JSON serialization"""
        robot = Robot(id="test-1", name="Test Robot", status="online")
        robot_dict = robot.model_dump()
        
        expected = {
            "id": "test-1",
            "name": "Test Robot",
            "status": "online"
        }
        assert robot_dict == expected
    
    def test_robot_from_dict(self):
        """Test creating robot from dictionary"""
        robot_data = {
            "id": "test-1",
            "name": "Test Robot",
            "status": "online"
        }
        robot = Robot(**robot_data)
        assert robot.id == "test-1"
        assert robot.name == "Test Robot"
        assert robot.status == "online"


class TestRobotUpdateModel:
    """Test suite for RobotUpdate model validation"""
    
    def test_valid_robot_update(self):
        """Test creating a valid robot update"""
        update = RobotUpdate(name="Updated Name", status="maintenance")
        assert update.name == "Updated Name"
        assert update.status == "maintenance"
    
    def test_partial_robot_update(self):
        """Test robot update with only some fields"""
        # Only name
        update = RobotUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.status is None
        
        # Only status
        update = RobotUpdate(status="offline")
        assert update.name is None
        assert update.status == "offline"
    
    def test_empty_robot_update(self):
        """Test robot update with no fields"""
        update = RobotUpdate()
        assert update.name is None
        assert update.status is None
    
    def test_robot_update_validation(self):
        """Test robot update field validation"""
        # Empty strings should be rejected
        with pytest.raises(ValidationError):
            RobotUpdate(name="")
        
        with pytest.raises(ValidationError):
            RobotUpdate(status="")
    
    def test_robot_update_types(self):
        """Test robot update field type validation"""
        with pytest.raises(ValidationError):
            RobotUpdate(name=123)
        
        with pytest.raises(ValidationError):
            RobotUpdate(status=123)