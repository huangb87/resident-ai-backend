from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_organization
from app.db.postgresql.models import WhatsAppUser, Organization
from pydantic import BaseModel

router = APIRouter()

class WhatsAppUserCreate(BaseModel):
    phone_number: str
    name: str = ""
    settings: dict = {}

class WhatsAppUserResponse(BaseModel):
    id: str
    phone_number: str
    name: str
    settings: dict
    organization_id: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=WhatsAppUserResponse)
async def create_whatsapp_user(
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
        name=user_data.name,
        settings=user_data.settings,
        organization_id=organization.id
    )
    
    db.add(whatsapp_user)
    db.commit()
    db.refresh(whatsapp_user)
    
    return whatsapp_user

@router.get("/", response_model=List[WhatsAppUserResponse])
async def get_whatsapp_users(
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    return db.query(WhatsAppUser).filter(
        WhatsAppUser.organization_id == organization.id
    ).all()

@router.get("/{user_id}", response_model=WhatsAppUserResponse)
async def get_whatsapp_user(
    user_id: str,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    user = db.query(WhatsAppUser).filter(
        WhatsAppUser.id == user_id,
        WhatsAppUser.organization_id == organization.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp user not found"
        )
    
    return user
