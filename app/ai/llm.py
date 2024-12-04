"""
LLM service for handling OpenAI interactions
"""
from typing import List, Optional, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage
)
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using the chat model
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            
        Returns:
            Generated response text
        """
        formatted_messages: List[BaseMessage] = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append(SystemMessage(content=system_prompt))
            
        # Format chat messages
        for message in messages:
            if message["role"] == "assistant":
                formatted_messages.append(AIMessage(content=message["content"]))
            elif message["role"] == "user":
                formatted_messages.append(HumanMessage(content=message["content"]))
                
        # Generate response
        response = await self.llm.agenerate([formatted_messages])
        return response.generations[0][0].text
        
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a message
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis
        """
        system_prompt = """
        Analyze the sentiment of the following text and return a JSON object with:
        - sentiment: (positive, negative, or neutral)
        - confidence: (float between 0 and 1)
        - key_emotions: (list of primary emotions detected)
        """
        
        messages = [{"role": "user", "content": text}]
        response = await self.generate_response(messages, system_prompt)
        
        # Parse response into structured format
        # Note: In production, add proper error handling
        import json
        return json.loads(response)
        
    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of entities with type and value
        """
        system_prompt = """
        Extract named entities from the following text and return a JSON array of objects with:
        - type: (person, organization, location, date, etc.)
        - value: (the extracted entity text)
        """
        
        messages = [{"role": "user", "content": text}]
        response = await self.generate_response(messages, system_prompt)
        
        # Parse response into structured format
        import json
        return json.loads(response)

    async def handle_user_query(self, query: str, context: List[Dict[str, str]]) -> str:
        """
        Handle a user query by generating a response using OpenAI's GPT model.
        
        Args:
            query: The user's query string.
            context: List of previous messages to maintain conversation flow.
            
        Returns:
            Generated response text.
        """
        # Add user query to the context
        context.append({"role": "user", "content": query})
        
        # Generate response
        response = await self.generate_response(context)
        
        # Add response to the context
        context.append({"role": "assistant", "content": response})
        
        return response
