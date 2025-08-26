# voice_assistant/views.py

import os
import asyncio
import logging
import traceback
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from livekit.api.access_token import AccessToken, VideoGrants
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# from .views_utils import simple_get_weather, simple_search_web  # helpers if you want to separate them
# If views_utils.py is in the same directory, use:
# from voice_assistant.views_utils import simple_get_weather, simple_search_web
# Or comment out if not needed:

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@api_view(["POST"])
@permission_classes([AllowAny])
def get_livekit_token(request):
    """
    POST { identity?: str, room?: str }
    →  { token: str, url: str }
    """
    try:
        data     = request.data
        identity = data.get("identity", "guest")
        room     = data.get("room",     "jarvis")

        # Get LiveKit URL from environment or use a default
        livekit_url = os.getenv("LIVEKIT_WS_URL", "wss://jarvis-w6b4irmm.livekit.cloud")
        
        # Check if LiveKit is properly configured
        if not os.getenv("LIVEKIT_API_KEY") or not os.getenv("LIVEKIT_API_SECRET"):
            return Response({
                "error": "LiveKit not configured. Please set LIVEKIT_API_KEY and LIVEKIT_API_SECRET in your .env file",
                "message": "LiveKit not configured - using mock token for development"
            }, status=400)

        # Build token with room-join grant
        try:
            # Set the API credentials for token generation
            api_key = os.getenv("LIVEKIT_API_KEY")
            api_secret = os.getenv("LIVEKIT_API_SECRET")
            
            at = (
                AccessToken(api_key=api_key, api_secret=api_secret)
                .with_identity(identity)
                .with_grants(VideoGrants(room_join=True, room=room))
            )

            token = at.to_jwt()
            logger.info(f"Generated LiveKit token for {identity} in room {room}")
            
            return Response({
                "token": token,
                "url": livekit_url,
            })
        except Exception as token_error:
            logger.error(f"Error generating LiveKit token: {token_error}")
            return Response({
                "error": "Failed to generate LiveKit token",
                "details": str(token_error)
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error generating LiveKit token: {str(e)}")
        logger.error(traceback.format_exc())
        # Return detailed error for debugging
        return Response({
            "error": f"LiveKit error: {str(e)}",
            "token": "fallback_token",
            "url": "wss://fallback-server.com",
            "message": "LiveKit error - using fallback mode"
        }, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def test_endpoint(request):
    return Response({"message": "Friday backend is working!", "status": "ok"})


@api_view(["POST"])
@permission_classes([AllowAny])
def voice_query(request):
    """
    Fallback text-based voice endpoint.
    POST { query: str }
    →  { response: str }
    """
    try:
        query = request.data.get("query", "").strip()
        if not query:
            return Response({"error":"Query is required"}, status=400)

        # very simple echo logic; swap in your real LLM or process_user_query
        response_text = f"I heard '{query}', sir. I can check weather or search the web."
        return Response({"response": response_text})

    except Exception as e:
        logger.error(traceback.format_exc())
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def voice_bot_status(request):
    """
    Test endpoint to check voice bot integration status
    """
    try:
        # Check if required environment variables are set
        livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
        livekit_url = os.getenv("LIVEKIT_WS_URL")
        
        status = {
            "voice_bot_status": "ready",
            "livekit_configured": bool(livekit_api_key and livekit_api_secret),
            "livekit_url": livekit_url,
            "message": "Voice bot integration is ready for Goldilocks questions"
        }
        
        if not livekit_api_key or not livekit_api_secret:
            status["voice_bot_status"] = "not_configured"
            status["message"] = "LiveKit API credentials not configured"
        
        return Response(status)
        
    except Exception as e:
        logger.error(f"Error checking voice bot status: {str(e)}")
        return Response({
            "voice_bot_status": "error",
            "error": str(e)
        }, status=500)


