# Function-based views for authentication using Kakao & Naver APIs
from datetime import date
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import unquote, urlencode
import requests

from api.models.user import Authentication, UserAuthentication, UserDetail
from backend import settings
from helper.types import AuthType


# Utils
def redirect_to_frontend(redirect_uri: str, query_params):
    """
    A custom redirect method
    """
    response = HttpResponse("", status=302)
    response["Location"] = f"{redirect_uri}?{urlencode(query_params)}"
    return response


# Kakao
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
    state = request.GET.get(
        "state"
    )  # for the frontend redirect uri + CSRF check (need to be same as the one we sent from FO to kakao api)
    frontend_redirect_uri = unquote(state)
    authorization_code = request.GET.get("code")  # from kakao GET api response
    auth_error_code = request.GET.get("error")  # error code from Kakao GET api
    auth_error_description = request.GET.get(
        "error_description", "Failed to retrieve authorization code"
    )

    # Step 2.1: Check any errors on fetching authorization code
    if auth_error_code or not authorization_code:
        return JsonResponse(
            {"error": auth_error_description}, status=500
        )  # for now, returning internal service error

    # Step 2.2: Make POST request
    base_url = f"{request.scheme}://{request.get_host()}"
    redirect_uri = f"{base_url}/api/auth/kakao/callback"  # need to be the current uri (to be matched with the first api)

    token_request_url = "https://kauth.kakao.com/oauth/token"
    token_request_body = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "client_secret": settings.KAKAO_REST_API_SECRET,
        "redirect_uri": redirect_uri,
        "code": authorization_code,
    }
    token_request_header = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    token_response = requests.post(
        token_request_url, data=token_request_body, headers=token_request_header
    )
    token_response_json = token_response.json()
    access_token = token_response_json.get("access_token")

    # Step 3. Handle the POST api response
    if not token_response.ok or not access_token:
        return JsonResponse(
            {"error": "Failed to retrieve access token"},
            status=token_response.status_code,
        )

    # Step 3.1: Retrieve current user info
    kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
    kakao_user_info_headers = {
        "Authorization": f"Bearer ${access_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    kakao_user_info_data = {"property_keys": '["kakao_account.profile"]'}

    user_info_response = requests.post(
        kakao_user_info_url, data=kakao_user_info_data, headers=kakao_user_info_headers
    )
    user_info_response_json = user_info_response.json()

    user_kakao_id = user_info_response_json.get("id")
    user_kakao_info = user_info_response_json.get("kakao_account")

    if not user_info_response.ok or not user_kakao_id:
        return JsonResponse(
            {"error": "Failed to retrieve user info"},
            status=user_info_response.status_code,
        )

    # Step 3.2: Check if the current user already exists
    # (Django model lookup will raise DoesNotExist or MultipleObjectsReturned)
    try:
        auth_item = Authentication.objects.get(
            provider_user_id=user_kakao_id, auth_type=AuthType.KAKAO
        )
        # If exists, then get the actual user ID
        if auth_item:
            print("User with this kakao account found")
            try:
                user_auth_item = UserAuthentication.objects.get(
                    auth_id=auth_item.auth_id
                )
                user_id = user_auth_item.user_id

                # If user_id found, then redirect to the frontend with status=existing
                if user_id:
                    return redirect_to_frontend(
                        frontend_redirect_uri,
                        {
                            "status": "existing",
                            "state": state,
                            "userId": user_id,
                            # TODO: additional params (token)
                        },
                    )
            except ObjectDoesNotExist:
                user_item = None
                try:
                    user_item = UserDetail.objects.get(
                        # TODO: check if we should bring the kakao profile image as well
                        username=user_kakao_info.get("profile").get("nickname")
                    )
                except ObjectDoesNotExist:
                    user_item = UserDetail.objects.create(
                        # TODO: check if we should bring the kakao profile image as well
                        username=user_kakao_info.get("profile").get("nickname")
                    )

                # New UserAuthentication object
                UserAuthentication.objects.create(user_id=user_item, auth_id=auth_item)

                return redirect_to_frontend(
                    frontend_redirect_uri,
                    {
                        "status": "new",
                        "state": state,
                        "userId": user_item.user_id,
                        # TODO: additional params
                    },
                )
    except ObjectDoesNotExist:
        print("User with this kakao account not found")
        # Otherwise, create a new user object
        # New Authentication object
        refresh_token = token_response_json.get("refresh_token")
        access_token_expires_in = token_response_json.get("expires_in", 0)
        refresh_token_expires_in = token_response_json.get(
            "refresh_token_expires_in", 0
        )

        new_auth = Authentication.objects.create(
            auth_type=AuthType.KAKAO,
            provider_user_id=user_kakao_id,
            provider_access_token=access_token,
            provider_refresh_token=refresh_token,
        )
        new_auth.set_token_expiration(access_token_expires_in, "access")
        new_auth.set_token_expiration(refresh_token_expires_in, "refresh")
        new_auth.save()

        # New UserDetail object
        new_user = UserDetail.objects.create(
            # TODO: check if we should bring the kakao profile image as well
            username=user_kakao_info.get("profile").get("nickname")
        )

        # # New UserAuthentication object
        UserAuthentication.objects.create(user_id=new_user, auth_id=new_auth)

        return redirect_to_frontend(
            frontend_redirect_uri,
            {
                "status": "new",
                "state": state,
                "userId": new_user.user_id,
                # TODO: check whether to create token for the new user as well
            },
        )

    except MultipleObjectsReturned:
        return JsonResponse(
            {"error": "Multiple users with the same account detected"},
            status=status.HTTP_409_CONFLICT,
        )


# Naver
