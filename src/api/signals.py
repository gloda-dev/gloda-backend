from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models.notification import EventNotification
from api.tasks import send_notification_task


@receiver(post_save, sender=EventNotification)
def trigger_event_notification(sender, instance, created, **kwargs):
    if created:
        send_notification_task.delay(instance.notification_id)
