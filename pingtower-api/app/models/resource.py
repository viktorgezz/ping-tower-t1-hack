from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    overall_status = Column(String, default="UNKNOWN")  # UP, DOWN, UNKNOWN
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    owner = relationship("User", back_populates="resources")
    endpoints = relationship("Endpoint", back_populates="resource", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="resource")

class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)  # GET, POST, PUT, DELETE, etc.
    current_status = Column(String, default="UNKNOWN")  # UP, DOWN, UNKNOWN
    incidents_24h = Column(Integer, default=0)
    last_response_time = Column(Integer, default=0)  # в миллисекундах
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    resource = relationship("Resource", back_populates="endpoints")
    logs = relationship("Log", back_populates="endpoint")
    selected_by_users = relationship("UserSelectedEndpoint", back_populates="endpoint")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    response_time = Column(Integer)  # в миллисекундах
    status = Column(String, nullable=False)  # SUCCESS, FAILED
    error_message = Column(String)
    
    # Связи
    resource = relationship("Resource", back_populates="logs")
    endpoint = relationship("Endpoint", back_populates="logs")
