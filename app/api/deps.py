from typing import Generator, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.postgresql.database import SessionLocal
from app.core.security import verify_token, verify_whatsapp_number
from app.db.postgresql.models import Organization, WhatsAppUser
from app.db.dynamodb.service import DynamoDBService

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_dynamodb() -> DynamoDBService:
    return DynamoDBService()

async def get_current_organization(
    db: Session = Depends(get_db),
    api_key: Optional[str] = Security(api_key_header)
) -> Organization:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    organization = db.query(Organization).filter(
        Organization.api_key == api_key,
        Organization.is_active == True
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return organization

async def verify_whatsapp_request(
    phone_number: str,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> WhatsAppUser:
    whatsapp_user = db.query(WhatsAppUser).filter(
        WhatsAppUser.phone_number == phone_number,
        WhatsAppUser.organization_id == organization.id,
        WhatsAppUser.is_active == True
    ).first()
    
    if not whatsapp_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="WhatsApp number not authorized"
        )
    
    return whatsapp_user

class RateLimiter:
    def __init__(self, limit_per_minute: int = 60):
        self.limit = limit_per_minute
        # Initialize Redis connection here
        
    async def check_rate_limit(
        self,
        key: str,
        organization: Organization = Depends(get_current_organization)
    ) -> bool:
        # Implement rate limiting logic using Redis
        # This is a placeholder that always returns True
        return True
