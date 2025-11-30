from django.db import models
import uuid
from helper.types import EventStatus
from api.models.user import UserDetail
from api.models.common import Location
from django_enum import EnumField


class EventDetail(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, max_length=200)
    main_image = models.BinaryField(blank=True)
    capacity = models.IntegerField()
    duration = models.IntegerField()  # in minutes
    status = EnumField(EventStatus, default=EventStatus.PLANNED)
    address = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)


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


class EventLogNotification(models.Model):
    notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_log_id = models.ForeignKey(EventLog, on_delete=models.CASCADE)
    detail = models.TextField(blank=True, max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)


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
