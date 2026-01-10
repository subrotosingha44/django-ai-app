"""
Services for AI operations.

This module contains service classes for handling AI-related operations.
"""
import os
from django.conf import settings
from openai import OpenAI


class AIService:
    """Service for AI operations using OpenAI"""
    
    def __init__(self):
        """Initialize AI service with OpenAI client"""
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in settings or environment")
        
        # Initialize OpenAI client
        # Handle httpx/proxies compatibility issues
        try:
            # Standard initialization for OpenAI SDK 1.x+
            self.client = OpenAI(api_key=api_key)
        except (TypeError, ValueError) as e:
            error_msg = str(e)
            # Handle proxies argument error (httpx version compatibility issue)
            if 'proxies' in error_msg:
                # Create custom httpx client without proxies to avoid version conflicts
                import httpx
                try:
                    # Try creating httpx client without proxies argument
                    # This handles httpx version differences
                    http_client = httpx.Client(timeout=60.0)
                    self.client = OpenAI(
                        api_key=api_key,
                        http_client=http_client,
                        timeout=60.0,
                        max_retries=2
                    )
                except TypeError:
                    # If httpx.Client also fails, try with minimal args
                    http_client = httpx.Client()
                    self.client = OpenAI(
                        api_key=api_key,
                        http_client=http_client
                    )
            else:
                # Re-raise if it's a different error
                raise Exception(f"Failed to initialize OpenAI client: {error_msg}")
        
        self.model = "gpt-4o-mini"
    
    def get_chat_response(self, message, system_prompt=None):
        """
        Get AI chat response.
        
        Args:
            message: User's message
            system_prompt: Optional system prompt
        
        Returns:
            AI response string
        """
        messages = []
        
        # Default system prompt for better structured responses
        default_system_prompt = """You are a helpful AI assistant. 
        When providing responses, use clear markdown formatting:
        - Use **bold** for important terms and headings
        - Use bullet points or numbered lists for multiple items
        - Use proper headings (##) for main sections
        - Keep responses well-structured and easy to read
        - Use line breaks between paragraphs for better readability"""
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": default_system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000  # Increased for longer, structured responses
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"AI service error: {str(e)}")

