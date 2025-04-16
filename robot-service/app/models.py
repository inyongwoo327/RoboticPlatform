from pydantic import BaseModel
from typing import Optional

class Robot(BaseModel):
    id: str
    name: str
    status: str

class RobotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None