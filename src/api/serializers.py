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


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["province", "city", "town"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_name", "main_image", "description"]


class SimpleUserDetailSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)

    class Meta:
        model = UserDetail
        fields = ["user_name", "bio", "profile_image", "location"]


class EventDetailSerializer(serializers.ModelSerializer):
    organizer = SimpleUserDetailSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = EventDetail
        fields = [
            "event_name",
            "description",
            "main_image",
            "capacity",
            "duration",
            "address",
            "organizer",
            "location",
            "category",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    events = EventDetailSerializer(many=True, read_only=True)

    class Meta:
        model = UserDetail
        fields = [
            "user_name",
            "bio",
            "invite_code",
            "profile_image",
            "date_of_birth",
            "time_created",
            "location",
            "events",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=True)

    class Meta:
        model = UserDetail
        fields = ["user_name", "bio", "profile_image", "date_of_birth", "location"]
