from typing import Dict, Optional
from datetime import datetime
import boto3
from app.core.config import settings

class DynamoDBClient:
    def __init__(self):
        self.client = boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url='http://localstack:4566'
        )

class ConversationModel:
    TABLE_NAME = "conversations"
    
    def __init__(self, dynamo_client: DynamoDBClient):
        self.table = dynamo_client.client.Table(self.TABLE_NAME)
    
    @classmethod
    def get_table_schema(cls) -> Dict:
        return {
            'TableName': cls.TABLE_NAME,
            'KeySchema': [
                {'AttributeName': 'phone_number', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'phone_number', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }

class MessageModel:
    TABLE_NAME = "messages"
    
    def __init__(self, dynamo_client: DynamoDBClient):
        self.table = dynamo_client.client.Table(self.TABLE_NAME)
    
    @classmethod
    def get_table_schema(cls) -> Dict:
        return {
            'TableName': cls.TABLE_NAME,
            'KeySchema': [
                {'AttributeName': 'conversation_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'phone_number', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'phone_number_index',
                    'KeySchema': [
                        {'AttributeName': 'phone_number', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }

class RateLimitModel:
    TABLE_NAME = "rate_limits"
    
    def __init__(self, dynamo_client: DynamoDBClient):
        self.table = dynamo_client.client.Table(self.TABLE_NAME)
    
    @classmethod
    def get_table_schema(cls) -> Dict:
        return {
            'TableName': cls.TABLE_NAME,
            'KeySchema': [
                {'AttributeName': 'key', 'KeyType': 'HASH'}  # phone_number or org_id
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'key', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
