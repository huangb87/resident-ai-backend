import boto3
import os
from app.db.dynamodb.models import ConversationModel, MessageModel, RateLimitModel
from app.core.config import settings

def create_table(dynamodb, schema):
    try:
        table = dynamodb.create_table(**schema)
        table.wait_until_exists()
        print(f"Created table {schema['TableName']}")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {schema['TableName']} already exists")
    except Exception as e:
        print(f"Error creating table {schema['TableName']}: {str(e)}")

def init_dynamodb():
    # Use LocalStack endpoint in development
    endpoint_url = os.getenv('DYNAMODB_ENDPOINT', None)
    
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=endpoint_url,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    # Create tables
    tables = [
        ConversationModel.get_table_schema(),
        MessageModel.get_table_schema(),
        RateLimitModel.get_table_schema()
    ]
    
    for table_schema in tables:
        create_table(dynamodb, table_schema)

if __name__ == "__main__":
    init_dynamodb()
