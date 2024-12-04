# WhatsApp AI Engine

A scalable WhatsApp-based Conversational AI system with multi-tenant support.

## Features

- WhatsApp integration with webhook support
- Multi-tenant architecture
- OpenAI-powered conversational AI
- Document processing and knowledge base management
- Hybrid database system (PostgreSQL + DynamoDB)
- Vector similarity search using Pinecone
- Rate limiting and authentication

## Tech Stack

- FastAPI
- PostgreSQL (User management & analytics)
- DynamoDB (Chat history & real-time data)
- Pinecone (Vector embeddings)
- Redis (Caching & rate limiting)
- LangChain (Document processing & chat chains)
- OpenAI (Language model)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your configuration:
   ```bash
   cp .env.example .env
   ```

5. Set up the databases:
   - PostgreSQL
   - DynamoDB tables
   - Pinecone index
   - Redis

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-2
AWS_ENDPOINT_URL=http://localstack:4566  # For local development

# Database Configuration
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=whatsapp-ai-engine
BACKEND_CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000"]

# Security
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
```
POST /api/v1/auth/login
- Login with email and password
- Returns JWT token

POST /api/v1/auth/register
- Register new organization
- Required fields: organization_name, email, password
```

### Conversations
```
POST /api/v1/conversations/
- Create new conversation
- Required fields: organization_id
- Optional fields: metadata

GET /api/v1/conversations/{conversation_id}
- Retrieve conversation details
- Returns conversation metadata and messages

GET /api/v1/conversations/
- List all conversations for organization
- Supports pagination and filtering

DELETE /api/v1/conversations/{conversation_id}
- Delete conversation and associated messages
```

### Messages
```
POST /api/v1/messages/
- Send message in conversation
- Required fields: conversation_id, content
- Optional fields: metadata

GET /api/v1/messages/{message_id}
- Retrieve message details

GET /api/v1/messages/conversation/{conversation_id}
- List all messages in conversation
- Supports pagination
```

### WhatsApp Webhook
```
POST /api/v1/webhook/whatsapp
- Receives WhatsApp messages and events
- Handles message processing and AI responses
```

## Project Structure

```
app/
├── api/
│   ├── v1/
│   │   ├── auth/         # Authentication endpoints
│   │   ├── chat/         # Chat handling endpoints
│   │   └── webhook/      # WhatsApp webhook
├── core/
│   ├── config/          # Environment & app configuration
│   ├── security/        # Authentication & authorization
│   └── logging/         # Logging configuration
├── db/
│   ├── dynamodb/        # DynamoDB models & operations
│   └── postgresql/      # PostgreSQL models & operations
├── services/
│   ├── ai/             # OpenAI integration
│   ├── chat/           # Chat processing
│   ├── knowledge_base/ # Document processing & embeddings
│   └── whatsapp/       # WhatsApp service integration
└── utils/              # Utility functions
```

## Database Schema

### PostgreSQL Tables
- organizations
- users
- api_keys
- webhooks
- analytics

### DynamoDB Tables
- conversations
  - Primary key: conversation_id
  - Sort key: organization_id
  
- messages
  - Primary key: message_id
  - Sort key: conversation_id
  
- rate_limits
  - Primary key: key
  - Sort key: timestamp

## Development

### Local Development with Docker

1. Start the services:
```bash
docker-compose up -d
```

2. Initialize the databases:
```bash
python scripts/init_db.py
```

3. Create test data (optional):
```bash
python scripts/create_test_data.py
```

### Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Production Deployment

1. Build the Docker images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Run the containers:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Monitor logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### CI/CD Integration

- Use GitHub Actions for automated testing and deployment.
- Define workflows in `.github/workflows/` directory.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [AWS SDK for Python (Boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
