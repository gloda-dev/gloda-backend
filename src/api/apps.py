from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"


class NotificationsConfig(AppConfig):
    name = "notifications"

    def ready(self):
        import src.api.signals
