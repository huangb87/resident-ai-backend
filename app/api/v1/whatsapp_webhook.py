"""
WhatsApp webhook endpoint for handling incoming messages
"""
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_organization
from app.db.postgresql.models import Organization, WhatsAppUser
from app.services.whatsapp_service import WhatsAppService
from app.core.config import settings

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Handle WhatsApp webhook verification
    """
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        # Verify token
        if mode and token:
            if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
                if challenge:
                    return Response(content=challenge, media_type="text/plain")
            
        raise HTTPException(status_code=403, detail="Invalid verification token")
        
    except Exception as e:
        print(f"Error verifying webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
):
    """
    Handle incoming WhatsApp webhook requests
    """
    try:
        # Parse the incoming webhook data
        webhook_data = await request.json()
        
        # Verify this is a WhatsApp message webhook
        if webhook_data.get("object") != "whatsapp_business_account":
            raise HTTPException(status_code=400, detail="Invalid webhook data")
            
        # Process each entry
        for entry in webhook_data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("value", {}).get("messages"):
                    for message in change["value"]["messages"]:
                        # Extract message details
                        phone_number = message.get("from")
                        message_text = message.get("text", {}).get("body", "")
                        
                        if phone_number and message_text:
                            # Initialize WhatsApp service
                            whatsapp_service = WhatsAppService(organization=organization)
                            
                            # Process the message
                            response = await whatsapp_service.process_message(message_text)
                            
                            # Send the response back to the user
                            await whatsapp_service.send_message(phone_number, response)
        
        return {"status": "success"}
        
    except Exception as e:
        # Log the error
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
