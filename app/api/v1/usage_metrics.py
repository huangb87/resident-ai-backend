from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_organization
from app.db.postgresql.models import UsageMetrics, Organization
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class UsageMetricCreate(BaseModel):
    metric_type: str
    value: float
    metadata: dict = {}

class UsageMetricResponse(BaseModel):
    id: str
    query_count: int
    token_count: int
    embedding_count: int
    extra_metadata: dict
    organization_id: str
    date: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=UsageMetricResponse)
async def create_usage_metric(
    metric_data: UsageMetricCreate,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    usage_metric = UsageMetrics(
        organization_id=organization.id,
        date=datetime.utcnow(),
        query_count=0,
        token_count=0,
        embedding_count=0,
        extra_metadata=metric_data.metadata
    )
    
    # Update the specific counter based on metric_type
    if metric_data.metric_type == "query":
        usage_metric.query_count = int(metric_data.value)
    elif metric_data.metric_type == "token":
        usage_metric.token_count = int(metric_data.value)
    elif metric_data.metric_type == "embedding":
        usage_metric.embedding_count = int(metric_data.value)
    
    db.add(usage_metric)
    db.commit()
    db.refresh(usage_metric)
    
    return usage_metric

@router.get("/", response_model=List[UsageMetricResponse])
async def get_usage_metrics(
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    return db.query(UsageMetrics).filter(
        UsageMetrics.organization_id == organization.id
    ).all()

@router.get("/by-type/{metric_type}", response_model=List[UsageMetricResponse])
async def get_usage_metrics_by_type(
    metric_type: str,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    metrics = db.query(UsageMetrics).filter(
        UsageMetrics.organization_id == organization.id
    )
    
    # Filter based on non-zero values for the specific metric type
    if metric_type == "query":
        metrics = metrics.filter(UsageMetrics.query_count > 0)
    elif metric_type == "token":
        metrics = metrics.filter(UsageMetrics.token_count > 0)
    elif metric_type == "embedding":
        metrics = metrics.filter(UsageMetrics.embedding_count > 0)
    
    return metrics.all()
