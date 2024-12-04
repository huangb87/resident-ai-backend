from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )
    return encoded_jwt

def verify_token(token: str) -> Union[dict, None]:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None

def verify_whatsapp_number(phone_number: str, organization_id: str) -> bool:
    # Implement WhatsApp number verification logic here
    # This could involve checking against your database or WhatsApp's API
    return True  # Placeholder return

class SecurityUtils:
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return pwd_context.hash(api_key)
    
    @staticmethod
    def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
        return pwd_context.verify(plain_api_key, hashed_api_key)
    
    @staticmethod
    def generate_api_key() -> str:
        # Generate a secure random API key
        import secrets
        return secrets.token_urlsafe(32)
