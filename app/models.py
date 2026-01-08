"""
Models for the app.

This module contains database models for the Django AI project.
"""
from django.db import models
from django.utils import timezone


class ChatMessage(models.Model):
    """Model for storing chat messages"""
    
    user_message = models.TextField(help_text="User's message")
    ai_response = models.TextField(help_text="AI's response", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"Message at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_message_preview(self):
        """Get preview of user message"""
        return self.user_message[:50] + "..." if len(self.user_message) > 50 else self.user_message

