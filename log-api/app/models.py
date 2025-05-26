from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    kubernetes: Optional[Dict[str, Any]] = None


class LogSearchResult(BaseModel):
    total: int
    logs: List[Dict[Any, Any]]
