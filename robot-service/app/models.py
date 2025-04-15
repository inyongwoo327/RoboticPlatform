from pydantic import BaseModel

class Robot(BaseModel):
    id: str
    name: str
    status: str

class RobotUpdate(BaseModel):
    name: str | None = None
    status: str | None = None