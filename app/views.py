"""
Views for the app.

This module contains views for the Django AI project.
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from .models import ChatMessage
from .services import AIService
import json


def home(request):
    """Home page view"""
    return render(request, 'home.html', {
        'title': 'AI Chat Application',
        'description': 'Welcome to the AI Chat Application'
    })


def health_check(request):
    """Health check endpoint for Render and monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'service': 'django-ai-app'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


@require_http_methods(["GET", "POST"])
def chat_view(request):
    """Chat interface view"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        try:
            # Get AI response
            ai_service = AIService()
            response = ai_service.get_chat_response(message)
            
            # Save to database
            chat_message = ChatMessage.objects.create(
                user_message=message,
                ai_response=response
            )
            
            return JsonResponse({
                'response': response,
                'message_id': chat_message.id
            })
        except ValueError as e:
            # Handle missing API key or initialization errors
            error_details = str(e)
            return JsonResponse({
                'error': error_details,
                'type': 'ConfigurationError',
                'hint': 'Please check your OPENAI_API_KEY in .env file'
            }, status=500)
        except Exception as e:
            # Log full error for debugging
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Chat view error: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return user-friendly error
            error_msg = str(e)
            return JsonResponse({
                'error': error_msg,
                'type': type(e).__name__
            }, status=500)
    
    # GET request - show chat interface
    messages = ChatMessage.objects.all()[:20]  # Last 20 messages
    return render(request, 'chat_ui.html', {
        'messages': messages,
        'title': 'Chat'
    })


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for chat"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get AI response
        ai_service = AIService()
        response = ai_service.get_chat_response(message)
        
        # Save to database
        chat_message = ChatMessage.objects.create(
            user_message=message,
            ai_response=response
        )
        
        return JsonResponse({
            'response': response,
            'message_id': chat_message.id,
            'created_at': chat_message.created_at.isoformat()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
        # Handle missing API key or initialization errors
        import traceback
        error_details = str(e)
        return JsonResponse({
            'error': error_details,
            'type': 'ConfigurationError',
            'hint': 'Please check your OPENAI_API_KEY in .env file'
        }, status=500)
    except Exception as e:
        # Log full error for debugging
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chat API error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return user-friendly error
        error_msg = str(e)
        return JsonResponse({
            'error': error_msg,
            'type': type(e).__name__
        }, status=500)

