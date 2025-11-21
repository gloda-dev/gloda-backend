from django.db import models
import uuid
from api.models.user import UserDetail
from api.models.event import EventDetail


class EventNotification(models.Model):
    notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    event_id = models.ForeignKey(EventDetail, on_delete=models.CASCADE)
    detail = models.TextField(blank=True, max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)


class UserNotification(models.Model):
    user_notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    notification_id = models.ForeignKey(EventNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
