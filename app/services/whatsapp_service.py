"""
WhatsApp message processing service
"""
from typing import Optional
import httpx
from app.ai.embeddings import PineconeService
from app.db.postgresql.models import WhatsAppUser, Organization
from app.core.config import settings

class WhatsAppService:
    def __init__(self, organization: Organization):
        self.organization = organization
        self.namespace = f"tenant_{organization.id}"
        self.pinecone_service = PineconeService(namespace=self.namespace)
        self.whatsapp_api_url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
    
    async def process_message(self, message: str) -> str:
        """
        Process incoming WhatsApp message and generate response
        
        Args:
            message: The incoming message text
            
        Returns:
            str: Response message to be sent back to the user
        """
        try:
            # Query Pinecone for relevant information
            results = await self.pinecone_service.similarity_search(query=message, k=4)
            
            if not results:
                return "I couldn't find any relevant information. Could you please rephrase your question?"
            
            # Extract the most relevant text
            most_relevant = results[0]
            response_text = most_relevant['metadata'].get('text', '')
            
            if not response_text:
                return "I found some information but couldn't process it properly. Please try again."
            
            return response_text
            
        except Exception as e:
            # Log the error
            print(f"Error processing message: {str(e)}")
            return "I encountered an error while processing your request. Please try again later."
    
    async def send_message(self, phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message to a user using the WhatsApp Business API
        
        Args:
            phone_number: The recipient's phone number
            message: The message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.whatsapp_api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"WhatsApp API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
