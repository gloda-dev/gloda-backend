from django.db import models
import uuid
from helper.types import AuthType
from api.models.common import Location
from django_enum import EnumField
from datetime import datetime


class UserDetail(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    bio = models.TextField(blank=True, max_length=100)
    invite_code = models.CharField(max_length=20)
    profile_image = models.BinaryField(blank=True)
    date_of_birth = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)
    username = models.CharField(
        max_length=30, blank=True
    )  # TODO: should be unique when put into use
    password_hash = models.CharField(max_length=128, blank=True)
    last_login = models.DateTimeField(default=datetime.now)


class UserLocation(models.Model):
    user_location_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class Authentication(models.Model):
    auth_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = EnumField(AuthType)
    token = models.CharField(blank=True, max_length=100)  ## TODO


class UserAuthentication(models.Model):
    user_auth_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    auth_id = models.ForeignKey(Authentication, on_delete=models.CASCADE)
