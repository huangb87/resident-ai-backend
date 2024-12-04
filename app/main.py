from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import (
    organizations,
    whatsapp_users,
    knowledge_bases,
    usage_metrics,
    conversations
)
from app.core.config import settings
from app.db.dynamodb.init_tables import init_dynamodb

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-tenant WhatsApp AI system with knowledge management",
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": str(exc)
            }
        )

# Initialize DynamoDB tables on startup
@app.on_event("startup")
async def startup_event():
    init_dynamodb()

# Include routers
app.include_router(
    organizations.router,
    prefix=f"{settings.API_V1_STR}/organizations",
    tags=["organizations"]
)

app.include_router(
    whatsapp_users.router,
    prefix=f"{settings.API_V1_STR}/whatsapp-users",
    tags=["whatsapp-users"]
)

app.include_router(
    knowledge_bases.router,
    prefix=f"{settings.API_V1_STR}/knowledge-bases",
    tags=["knowledge-bases"]
)

app.include_router(
    usage_metrics.router,
    prefix=f"{settings.API_V1_STR}/usage-metrics",
    tags=["usage-metrics"]
)

app.include_router(
    conversations.router,
    prefix=f"{settings.API_V1_STR}/conversations",
    tags=["conversations"]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
