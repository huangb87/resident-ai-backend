from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WhatsAppUser(Base):
    __tablename__ = "whatsapp_users"
    
    phone_number = Column(String, primary_key=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), onupdate=func.now())

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    vector_store_ids = Column(JSON, nullable=True)  # Store Pinecone namespace/ids
    extra_metadata = Column(JSON, nullable=True)  # Renamed from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UsageMetrics(Base):
    __tablename__ = "usage_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    query_count = Column(Integer, default=0)
    token_count = Column(Integer, default=0)
    embedding_count = Column(Integer, default=0)
    extra_metadata = Column(JSON, nullable=True)  # Renamed from metadata
