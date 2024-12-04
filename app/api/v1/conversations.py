from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from app.api.deps import get_dynamodb, get_current_organization, get_llm_service
from app.db.dynamodb.service import DynamoDBService
from app.db.postgresql.models import Organization
from app.core.logging import get_logger, log_api_call, log_error

router = APIRouter()
logger = get_logger(__name__)

class MessageCreate(BaseModel):
    content: str
    role: str
    metadata: dict = {}

class MessageResponse(BaseModel):
    conversation_id: str
    timestamp: str
    content: str
    role: str
    metadata: dict

class ConversationCreate(BaseModel):
    metadata: dict = {}

class ConversationResponse(BaseModel):
    phone_number: str
    timestamp: str
    metadata: dict

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    organization: Organization = Depends(get_current_organization),
    dynamodb: DynamoDBService = Depends(get_dynamodb)
):
    """Create a new conversation for a WhatsApp user."""
    try:
        log_api_call(logger, "/conversations", "POST", org_id=organization.id)
        
        phone_number = organization.settings.get("whatsapp_phone_number")
        if not phone_number:
            log_error(logger, Exception("Organization WhatsApp phone number not configured"), "create_conversation")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization WhatsApp phone number not configured"
            )
        
        conversation = await dynamodb.create_conversation(
            phone_number=phone_number,
            metadata={
                **data.metadata,
                "organization_id": str(organization.id)
            }
        )
        log_api_call(logger, "/conversations", "POST", org_id=organization.id, response_status=201)
        return conversation
    except Exception as e:
        log_error(logger, e, "create_conversation")
        raise

@router.get("/{phone_number}/{timestamp}", response_model=ConversationResponse)
async def get_conversation(
    phone_number: str,
    timestamp: str,
    organization: Organization = Depends(get_current_organization),
    dynamodb: DynamoDBService = Depends(get_dynamodb)
):
    """Get a specific conversation by phone number and timestamp."""
    try:
        log_api_call(
            logger,
            f"/conversations/{phone_number}/{timestamp}",
            "GET",
            org_id=organization.id
        )
        
        conversation = await dynamodb.get_conversation(phone_number, timestamp)
        if not conversation:
            log_error(logger, Exception("Conversation not found"), "get_conversation")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        if conversation.get("metadata", {}).get("organization_id") != str(organization.id):
            log_error(logger, Exception("Not authorized to access this conversation"), "get_conversation")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )
        
        log_api_call(
            logger,
            f"/conversations/{phone_number}/{timestamp}",
            "GET",
            org_id=organization.id,
            response_status=200
        )
        return conversation
    except Exception as e:
        log_error(logger, e, "get_conversation")
        raise

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    message: MessageCreate,
    organization: Organization = Depends(get_current_organization),
    dynamodb: DynamoDBService = Depends(get_dynamodb)
):
    """Add a message to an existing conversation."""
    try:
        log_api_call(
            logger,
            f"/conversations/{conversation_id}/messages",
            "POST",
            org_id=organization.id
        )
        
        conversation = await dynamodb.get_conversation(
            conversation_id.split(":")[0],
            conversation_id.split(":")[1]
        )
        if not conversation:
            log_error(logger, Exception("Conversation not found"), "create_message")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        if conversation.get("metadata", {}).get("organization_id") != str(organization.id):
            log_error(logger, Exception("Not authorized to access this conversation"), "create_message")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )
        
        message_data = await dynamodb.create_message(
            conversation_id=conversation_id,
            content=message.content,
            role=message.role,
            metadata={
                **message.metadata,
                "organization_id": str(organization.id)
            }
        )
        log_api_call(
            logger,
            f"/conversations/{conversation_id}/messages",
            "POST",
            org_id=organization.id,
            response_status=201
        )
        return message_data
    except Exception as e:
        log_error(logger, e, "create_message")
        raise

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    organization: Organization = Depends(get_current_organization),
    dynamodb: DynamoDBService = Depends(get_dynamodb)
):
    """Get all messages in a conversation."""
    try:
        log_api_call(
            logger,
            f"/conversations/{conversation_id}/messages",
            "GET",
            org_id=organization.id
        )
        
        conversation = await dynamodb.get_conversation(
            conversation_id.split(":")[0],
            conversation_id.split(":")[1]
        )
        if not conversation:
            log_error(logger, Exception("Conversation not found"), "get_conversation_messages")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        if conversation.get("metadata", {}).get("organization_id") != str(organization.id):
            log_error(logger, Exception("Not authorized to access this conversation"), "get_conversation_messages")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )
        
        messages = await dynamodb.get_conversation_messages(conversation_id)
        log_api_call(
            logger,
            f"/conversations/{conversation_id}/messages",
            "GET",
            org_id=organization.id,
            response_status=200
        )
        return messages
    except Exception as e:
        log_error(logger, e, "get_conversation_messages")
        raise

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    dynamodb: DynamoDBService = Depends(get_dynamodb),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Webhook endpoint to receive messages from WhatsApp and send responses back.
    """
    data = await request.json()
    message = data.get("message", {})
    sender = message.get("from")
    content = message.get("text", {}).get("body", "")
    
    # Parse incoming message
    if not sender or not content:
        raise HTTPException(status_code=400, detail="Invalid message format.")
    
    # Retrieve conversation context from DynamoDB
    conversation_id = f"{sender}_conversation"
    conversation = await dynamodb.get_conversation(conversation_id)
    context = conversation.get("messages", []) if conversation else []
    
    # Generate response using AI
    response_text = await llm_service.handle_user_query(content, context)
    
    # Update conversation context
    context.append({"role": "user", "content": content})
    context.append({"role": "assistant", "content": response_text})
    await dynamodb.update_conversation(conversation_id, {"messages": context})
    
    # Send response back to WhatsApp
    response_data = {
        "to": sender,
        "text": {
            "body": response_text
        }
    }
    
    # Placeholder for sending response back to WhatsApp API
    # send_to_whatsapp_api(response_data)
    
    return JSONResponse(content={"status": "success", "response": response_data})
