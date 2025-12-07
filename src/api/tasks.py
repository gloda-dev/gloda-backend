from celery import shared_task
from src.api.models.user import UserDetail
from src.api.models.event import UserEvent
from src.api.models.notification import UserNotification, EventNotification
from django.utils import timezone
import requests
import json

EXPO_URL = "https://exp.host/--/api/v2/push/send"  ## TODO: placeholder


def send_push_notification(token, title, message):
    body = {
        "to": token,
        "title": title,
        "body": message,
    }

    requests.post(EXPO_URL, json=body)


@shared_task
def send_notification_task(event_notification):
    try:
        # send notif to all users enrolled in the event
        event_notif = EventNotification.objects.get(pk=event_notification)
        participants = UserEvent.objects.filter(event_id=event_notif.event_id)
        for participant in participants:
            user = UserDetail.objects.get(pk=participant.user_id)

            UserNotification.objects.create(
                user_id=user.user_id,
                notification_id=event_notif,
            )

            token = user.expo_push_token
            if token:
                message = json.dumps(
                    {
                        "event_notification_id": str(event_notif.notification_id),
                        "event_id": str(event_notif.event_id.event_id),
                        "detail": event_notif.detail,
                        "time_created": event_notif.time_created.isoformat(),
                        "from_admin": event_notif.from_admin,
                    }
                )
                send_push_notification(
                    token,
                    f"New update for event {event_notif.event_id.event_name}",
                    message,
                )

        return f"EventNotification {event_notification} sent to users {[p.user_id for p in participants]} successfully"

    except event_notification.DoesNotExist:
        return f"EventNotification {event_notification} does not exist"
