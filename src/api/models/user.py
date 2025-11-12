from django.db import models
import uuid
from helper import AuthType
from api.models.common import Location
from api.models.event import EventDetail


class UserDetail(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=20)
    bio = models.TextField(blank=True, max_length=100)
    invite_code = models.CharField(max_length=20)
    profile_image = models.BinaryField(blank=True)
    date_of_birth = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)


class UserLocation(models.Model):
    user_location_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class Authentication(models.Model):
    auth_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(choices=AuthType.choices())
    token = models.CharField(blank=True, max_length=100)  ## TODO


class UserAuthentication(models.Model):
    user_auth_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    auth_id = models.ForeignKey(Authentication, on_delete=models.CASCADE)


class UserEvent(models.Model):
    user_event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    time_joined = models.DateTimeField(auto_now_add=True)


class UserEventLog(models.Model):
    user_event_log_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_event_id = models.ForeignKey(UserEvent, on_delete=models.CASCADE)
    has_checked_in = models.BooleanField(default=False)
