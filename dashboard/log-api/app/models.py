from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LogEntry(BaseModel):
    log: str
    stream: str
    time: str
    kubernetes: Optional[Dict[str, Any]] = None

class LogSearchResult(BaseModel):
    total: int
    logs: List[Dict[Any, Any]]