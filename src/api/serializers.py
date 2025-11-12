from rest_framework import serializers
from api.models.user import (
    UserDetail,
    UserLocation,
    UserAuthentication,
)
from api.models.common import Location
from api.models.event import (
    EventDetail,
    Category,
    EventCategory,
    EventLocation,
    EventLog,
    EventOrganizer,
    EventLogNotification,
    UserEvent,
    UserEventLog,
)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = "__all__"


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = "__all__"


class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthentication
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDetail
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = "__all__"


class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLocation
        fields = "__all__"


class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = "__all__"


class EventOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventOrganizer
        fields = "__all__"


class EventLogNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLogNotification
        fields = "__all__"


class UserEventSerializer(serializers.Serializer):
    class Meta:
        model = UserEvent
        fields = "__all__"


class UserEventLogSerializer(serializers.Serializer):
    class Meta:
        model = UserEventLog
        fields = "__all__"
