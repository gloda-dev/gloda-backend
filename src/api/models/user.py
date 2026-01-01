from django.db import models
import uuid
from helper.types import AuthType
from api.models.common import Location
from django_enum import EnumField
from datetime import datetime, timedelta
from django.utils import timezone


class UserDetail(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    bio = models.TextField(blank=True, max_length=100)
    invite_code = models.CharField(max_length=20)
    profile_image = models.BinaryField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True) # probably better to remove this one
    age_range = models.CharField(max_length=20, blank=True, null=True) # e.g. 20-29, 30-39, 40-49
    time_created = models.DateTimeField(auto_now_add=True)
    username = models.CharField(
        max_length=30, blank=True
    )  # TODO: should be unique when put into use
    password_hash = models.CharField(max_length=128, blank=True)
    last_login = models.DateTimeField(default=datetime.now)
    expo_push_token = models.CharField(max_length=255, blank=True, null=True)


class UserLocation(models.Model):
    user_location_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class Authentication(models.Model):
    auth_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_type = EnumField(AuthType)
    provider_user_id = models.TextField(blank=True) # TODO: check whether to remove this field?
    provider_access_token = models.TextField(blank=True)
    provider_access_token_expires_at = models.DateTimeField(null=True, blank=True)
    provider_refresh_token = models.TextField(blank=True)
    provider_refresh_token_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('auth_type', 'provider_user_id')]

    def set_token_expiration(self, expires_in_seconds, token_type='access'):
        """
        Helper method to convert Kakao's expires_in (integer seconds) to DateTime.
        Sets expiration based on current time (timezone.now()).
        Usage: auth.set_token_expiration(21600, 'access')
        """
        if expires_in_seconds:
            expiration_time = timezone.now() + timedelta(seconds=expires_in_seconds)
            if token_type == 'access':
                self.provider_access_token_expires_at = expiration_time
            elif token_type == 'refresh':
                self.provider_refresh_token_expires_at = expiration_time

    def is_access_token_expired(self):
        """Check if access token has expired."""
        if not self.provider_access_token_expires_at:
            return True
        return timezone.now() >= self.provider_access_token_expires_at

    def is_refresh_token_expired(self):
        """Check if refresh token has expired."""
        if not self.provider_refresh_token_expires_at:
            return False  # If no expiration set, assume not expired
        return timezone.now() >= self.provider_refresh_token_expires_at


class UserAuthentication(models.Model):
    user_auth_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    auth_id = models.ForeignKey(Authentication, on_delete=models.CASCADE)
