from pydantic import BaseModel, field_validator
from typing import Optional

class Robot(BaseModel):
    id: str
    name: str
    status: str
    
    @field_validator('id', 'name', 'status')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace')
        return v

class RobotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('name', 'status')
    @classmethod
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or whitespace')
        return v