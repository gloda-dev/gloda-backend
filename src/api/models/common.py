from django.db import models
import uuid


class Location(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    province = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    description = models.TextField(blank=True, max_length=100)
