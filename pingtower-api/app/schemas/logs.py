from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class LogEntry(BaseModel):
    id: UUID
    timestamp: datetime
    resourceId: UUID
    resourceName: str
    endpointId: UUID
    path: str
    method: str
    statusCode: int
    responseTime: int
    status: str
    errorMessage: Optional[str] = None

class LogsResponse(BaseModel):
    logs: List[LogEntry]
    totalCount: int

class LogAnalysis(BaseModel):
    analysis: str
    relatedLogs: List[str]

class LogsQueryParams(BaseModel):
    resourceId: Optional[UUID] = None
    endpointId: Optional[UUID] = None
    status: Optional[str] = None
    from_: Optional[datetime] = None
    to: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
