from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class NotificationChannel(Base):
    __tablename__ = "notification_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # EMAIL, TELEGRAM, SLACK, etc.
    value = Column(String, nullable=False)  # email address, telegram username, etc.
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="notification_channels")

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    conditions = Column(JSON, nullable=False)  # {"statusCode": [500, 502], "timeout": 5000}
    channels = Column(JSON, nullable=False)  # ["channel_1", "channel_2"]
    delay = Column(Integer, default=0)  # задержка в секундах
    repeat_interval = Column(Integer, default=300)  # интервал повтора в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="alert_rules")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sent_at = Column(DateTime, default=datetime.utcnow)
    channel_type = Column(String, nullable=False)
    channel_value = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    resource_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
