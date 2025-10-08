from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ResourceCreate(BaseModel):
    name: str
    url: HttpUrl

class EndpointInfo(BaseModel):
    id: UUID
    path: str
    method: str
    currentStatus: str
    incidents24h: int
    lastResponseTime: int

class ResourceMetrics(BaseModel):
    uptime24h: str
    avgResponseTime: int
    incidents24h: int
    lastCheck: datetime

class ResourceResponse(BaseModel):
    id: UUID
    name: str
    url: str
    overallStatus: str
    metrics: ResourceMetrics

class ResourcesListResponse(BaseModel):
    resources: List[ResourceResponse]

class EndpointDiscovery(BaseModel):
    path: str
    method: str
    isSelected: bool

class EndpointDiscoveryResponse(BaseModel):
    endpoints: List[EndpointDiscovery]

class EndpointUpdate(BaseModel):
    path: str
    method: str

class EndpointsUpdate(BaseModel):
    endpoints: List[EndpointUpdate]

# Схемы для создания эндпоинтов
class EndpointCreate(BaseModel):
    path: str
    method: str

class EndpointsCreateRequest(BaseModel):
    resource_id: UUID
    endpoints: List[EndpointCreate]

class EndpointResponse(BaseModel):
    id: UUID
    path: str
    method: str
    current_status: str
    incidents_24h: int
    last_response_time: int
    created_at: datetime

class EndpointsCreateResponse(BaseModel):
    message: str
    resource_id: UUID
    created_count: int
    endpoints: List[EndpointResponse]

class ResourceDetailResponse(BaseModel):
    id: UUID
    name: str
    url: str
    endpoints: List[EndpointInfo]

class StatsDataPoint(BaseModel):
    timestamp: datetime
    value: int

class StatsResponse(BaseModel):
    period: str
    data: List[StatsDataPoint]
