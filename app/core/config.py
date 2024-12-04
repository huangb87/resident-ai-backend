from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "WhatsApp AI Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    # DynamoDB
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    
    # WhatsApp
    WHATSAPP_API_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
