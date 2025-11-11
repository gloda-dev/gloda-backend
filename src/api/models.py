from django.db import models
import uuid
from enum import StrEnum


class UserDetail(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=20)
    bio = models.TextField(blank=True, max_length=100)
    invite_code = models.CharField(max_length=20)
    profile_image = models.BinaryField(blank=True)
    date_of_birth = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    province = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    description = models.TextField(blank=True, max_length=100)


class UserLocation(models.Model):
    user_location_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class AuthType(StrEnum):
    KAKAO = "kakao"
    NAVER = "naver"
    ## PASS = "pass"


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


class EventStatus(StrEnum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventDetail(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, max_length=200)
    main_image = models.BinaryField(blank=True)
    max_participants = models.IntegerField()
    duration = models.IntegerField()  # in minutes
    status = models.CharField(choices=EventStatus.choices())
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)


class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=20)
    main_image = models.BinaryField(blank=True)
    description = models.TextField(blank=True, max_length=100)


class EventCategory(models.Model):
    event_category_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)


class EventLocation(models.Model):
    event_location_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)


class EventLog(models.Model):
    event_log_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    description = models.TextField(blank=True, max_length=100)


class EventOrganizer(models.Model):
    event_organizer_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)


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


class EventLogNotification(models.Model):
    notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_log_id = models.ForeignKey(EventLog, on_delete=models.CASCADE)
    detail = models.TextField(blank=True, max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)
