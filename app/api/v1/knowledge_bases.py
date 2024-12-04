from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_organization
from app.db.postgresql.models import KnowledgeBase, Organization
from pydantic import BaseModel

router = APIRouter()

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""
    settings: dict = {}

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str
    settings: dict
    organization_id: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    knowledge_base = KnowledgeBase(
        name=kb_data.name,
        description=kb_data.description,
        settings=kb_data.settings,
        organization_id=organization.id
    )
    
    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)
    
    return knowledge_base

@router.get("/", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_bases(
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    return db.query(KnowledgeBase).filter(
        KnowledgeBase.organization_id == organization.id
    ).all()

@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.organization_id == organization.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    return knowledge_base
