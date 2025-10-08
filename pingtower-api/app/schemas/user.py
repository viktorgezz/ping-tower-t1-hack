from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class UserProfile(BaseModel):
    id: UUID
    email: str
    name: str
    emailVerified: bool

class UserProfileUpdate(BaseModel):
    name: str

class NotificationChannel(BaseModel):
    id: UUID
    type: str
    value: str
    verified: bool

class NotificationChannelsResponse(BaseModel):
    channels: List[NotificationChannel]

class NotificationChannelCreate(BaseModel):
    type: str
    value: str

class AlertRuleConditions(BaseModel):
    statusCode: List[int]
    timeout: int

class AlertRule(BaseModel):
    id: UUID
    name: str
    isActive: bool
    conditions: AlertRuleConditions
    channels: List[str]
    delay: int
    repeatInterval: int

class AlertRulesResponse(BaseModel):
    rules: List[AlertRule]

class AlertRuleCreate(BaseModel):
    name: str
    isActive: bool
    conditions: AlertRuleConditions
    channels: List[str]
    delay: int
    repeatInterval: int

class AlertRuleUpdate(BaseModel):
    name: str
    isActive: bool
    conditions: AlertRuleConditions
    channels: List[str]
    delay: int
    repeatInterval: int

class NotificationLog(BaseModel):
    id: UUID
    sentAt: datetime
    channelType: str
    channelValue: str
    ruleName: str
    resourceName: str
    message: str

class NotificationLogsResponse(BaseModel):
    notifications: List[NotificationLog]
    totalCount: int

class NotificationLogsQueryParams(BaseModel):
    type: Optional[str] = None
    from_: Optional[datetime] = None
    to: Optional[datetime] = None
    limit: int = 50
    offset: int = 0

# Схемы для выбранных эндпоинтов
class SelectedEndpoint(BaseModel):
    endpoint_id: UUID
    is_selected: bool

class SaveSelectedEndpointsRequest(BaseModel):
    resource_id: UUID
    selected_endpoints: List[SelectedEndpoint]

class UserSelectedEndpointResponse(BaseModel):
    id: UUID
    endpoint_id: UUID
    is_active: bool
    created_at: datetime
    endpoint_path: str
    endpoint_method: str

class SelectedEndpointsResponse(BaseModel):
    selected_endpoints: List[UserSelectedEndpointResponse]