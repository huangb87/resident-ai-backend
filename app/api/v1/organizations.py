from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_organization
from app.core.security import SecurityUtils
from app.db.postgresql.models import Organization, WhatsAppUser
from pydantic import BaseModel, EmailStr

router = APIRouter()

class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr
    settings: dict = {}

class OrganizationResponse(BaseModel):
    id: str
    name: str
    api_key: str
    settings: dict
    
    class Config:
        from_attributes = True

class WhatsAppUserCreate(BaseModel):
    phone_number: str
    settings: dict = {}

class WhatsAppUserResponse(BaseModel):
    id: str
    phone_number: str
    settings: dict
    organization_id: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    api_key = SecurityUtils.generate_api_key()
    
    organization = Organization(
        name=org_data.name,
        api_key=api_key,
        settings=org_data.settings
    )
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    return organization

@router.post("/whatsapp-users", response_model=WhatsAppUserResponse)
async def add_whatsapp_user(
    user_data: WhatsAppUserCreate,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    # Check if phone number is already registered
    existing_user = db.query(WhatsAppUser).filter(
        WhatsAppUser.phone_number == user_data.phone_number
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    whatsapp_user = WhatsAppUser(
        phone_number=user_data.phone_number,
        organization_id=organization.id,
        settings=user_data.settings
    )
    
    db.add(whatsapp_user)
    db.commit()
    db.refresh(whatsapp_user)
    
    return whatsapp_user

@router.get("/whatsapp-users", response_model=List[WhatsAppUserResponse])
async def get_organization_whatsapp_users(
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    return db.query(WhatsAppUser).filter(
        WhatsAppUser.organization_id == organization.id
    ).all()
