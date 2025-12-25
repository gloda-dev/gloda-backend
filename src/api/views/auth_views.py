# Function-based views for authentication using Kakao & Naver APIs
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

def kakao_redirect(request: HttpRequest) -> HttpResponse:
    """
    Once receiving the authorization code from Kakao, this function will:
    - extract request parameters (state, a.k.a. frontend redirect uri, (authorization) code, error)
    - call POST `https://kauth.kakao.com/oauth/token` api to retrieve access & refresh token
    
    Once receiving the token from Kakao, this function will:
    - extract access & refresh tokens and all its relevant info
    - call GET `https://kapi.kakao.com/v2/user/me` to fetch the current user's info
    - based on this info, if the user is already existing, then redirect to the frontend_redirect_uri?status="existing"
    - otherwise, it will redirect to status="new"
    - in case of error, it will throw an exception

    """
    # Step 1: Parse request parameters
    return None

# Helper function?
def kakao_handle_token(request: HttpRequest) -> HttpResponse:
    """
    
    """
    return None

