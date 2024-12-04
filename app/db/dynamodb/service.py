from typing import List, Optional, Dict
from datetime import datetime
from app.db.dynamodb.models import (
    DynamoDBClient,
    ConversationModel,
    MessageModel,
    RateLimitModel
)

class DynamoDBService:
    def __init__(self):
        self.client = DynamoDBClient()
        self.conversations = ConversationModel(self.client)
        self.messages = MessageModel(self.client)
        self.rate_limits = RateLimitModel(self.client)
    
    async def create_conversation(self, phone_number: str, metadata: Dict = None) -> Dict:
        timestamp = datetime.utcnow().isoformat()
        item = {
            'phone_number': phone_number,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        self.conversations.table.put_item(Item=item)
        return item
    
    async def get_conversation(self, phone_number: str, timestamp: str) -> Optional[Dict]:
        response = await self.conversations.table.get_item(
            Key={
                'phone_number': phone_number,
                'timestamp': timestamp
            }
        )
        return response.get('Item')
    
    async def create_message(self, conversation_id: str, content: str, role: str, metadata: Dict = None) -> Dict:
        timestamp = datetime.utcnow().isoformat()
        item = {
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'content': content,
            'role': role,
            'metadata': metadata or {}
        }
        await self.messages.table.put_item(Item=item)
        return item
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        response = await self.messages.table.query(
            KeyConditionExpression='conversation_id = :cid',
            ExpressionAttributeValues={
                ':cid': conversation_id
            }
        )
        return response.get('Items', [])
    
    async def update_rate_limit(self, key: str, window_start: str, count: int) -> None:
        item = {
            'key': key,
            'window_start': window_start,
            'count': count
        }
        await self.rate_limits.table.put_item(Item=item)
    
    async def get_rate_limit(self, key: str, window_start: str) -> Optional[Dict]:
        response = await self.rate_limits.table.get_item(
            Key={
                'key': key,
                'window_start': window_start
            }
        )
        return response.get('Item')
