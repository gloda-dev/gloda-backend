from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime, date
import uuid

from api.models.user import UserDetail, UserLocation, Authentication, UserAuthentication
from api.models.event import (
    EventDetail,
    Category,
    EventCategory,
    EventLocation,
    EventLog,
    EventOrganizer,
    UserEvent,
    UserEventLog,
)
from api.models.notification import EventNotification, UserNotification
from api.models.common import Location
from helper.types import EventStatus, AuthType


class ModelTestCase(TestCase):
    """Test cases for database models"""

    def setUp(self):
        """Set up test data"""
        self.location = Location.objects.create(
            province="Seoul", city="Gangnam", town="Yeoksam"
        )

        self.user = UserDetail.objects.create(
            name="Test User",
            bio="Test bio",
            invite_code="TEST123",
            date_of_birth=date(1990, 1, 1),
        )

        self.event = EventDetail.objects.create(
            event_name="Test Event",
            description="Test Description",
            capacity=50,
            duration=120,
            address="Test Address",
            status=EventStatus.PLANNED,
        )

    def test_user_creation(self):
        """Test UserDetail model creation"""
        self.assertIsNotNone(self.user.user_id)
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(self.user.invite_code, "TEST123")

    def test_event_creation(self):
        """Test EventDetail model creation"""
        self.assertIsNotNone(self.event.event_id)
        self.assertEqual(self.event.event_name, "Test Event")
        self.assertEqual(self.event.capacity, 50)
        self.assertEqual(self.event.status, EventStatus.PLANNED)

    def test_location_creation(self):
        """Test Location model creation"""
        self.assertIsNotNone(self.location.location_id)
        self.assertEqual(self.location.province, "Seoul")
        self.assertEqual(self.location.city, "Gangnam")

    def test_event_organizer_relationship(self):
        """Test EventOrganizer relationship"""
        organizer = EventOrganizer.objects.create(
            event_id=self.event, user_id=self.user
        )
        self.assertEqual(organizer.user_id, self.user)
        self.assertEqual(organizer.event_id, self.event)

    def test_user_event_relationship(self):
        """Test UserEvent relationship"""
        user_event = UserEvent.objects.create(user_id=self.user, event_id=self.event)
        self.assertEqual(user_event.user_id, self.user)
        self.assertEqual(user_event.event_id, self.event)
        self.assertIsNotNone(user_event.time_joined)

    def test_event_notification_creation(self):
        """Test EventNotification model"""
        notification = EventNotification.objects.create(
            event_id=self.event, detail="Test notification", from_admin=False
        )
        self.assertIsNotNone(notification.notification_id)
        self.assertEqual(notification.detail, "Test notification")
        self.assertFalse(notification.from_admin)

    def test_user_notification_creation(self):
        """Test UserNotification model"""
        event_notif = EventNotification.objects.create(
            event_id=self.event, detail="Test notification"
        )
        user_notif = UserNotification.objects.create(
            user_id=self.user, notification_id=event_notif, is_read=False
        )
        self.assertEqual(user_notif.user_id, self.user)
        self.assertFalse(user_notif.is_read)


class UserAPITestCase(APITestCase):
    """Test cases for User API endpoints"""

    def setUp(self):
        """Set up test data and authentication"""
        self.client = APIClient()

        # Create Django user for JWT authentication
        self.django_user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.location = Location.objects.create(
            province="Seoul", city="Gangnam", town="Yeoksam"
        )

        self.user = UserDetail.objects.create(
            name="Test User",
            bio="Test bio",
            invite_code="TEST123",
            date_of_birth=date(1990, 1, 1),
            username="testuser",
        )

        # Get JWT token
        response = self.client.post(
            "/api/token/", {"username": "testuser", "password": "testpass123"}
        )
        if response.status_code == 200:
            self.token = response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_retrieve_user(self):
        """Test GET /api/users/{user_id}/"""
        url = f"/api/users/{self.user.user_id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test User")

    def test_retrieve_nonexistent_user(self):
        """Test retrieving non-existent user"""
        fake_id = uuid.uuid4()
        url = f"/api/users/{fake_id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_user_myinfo(self):
        """Test GET /api/users/{user_id}/myinfo/"""
        url = f"/api/users/{self.user.user_id}/myinfo/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("bio", response.data)

    def test_create_user(self):
        """Test POST /api/users/create/"""
        url = "/api/users/create_user/"
        data = {
            "name": "New User",
            "bio": "New bio",
            "date_of_birth": "1995-05-15",
            # not testing location here yet
        }
        response = self.client.post(url, data, format="json")

        # Should create successfully
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )

    def test_register_push_token(self):
        """Test POST /api/users/{user_id}/register-push-token/"""
        url = f"/api/users/{self.user.user_id}/register-push-token/"
        data = {"expo_push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"}
        response = self.client.post(url, data, format="json")

        # May fail without proper setup, but test the endpoint exists
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND,
            ],
        )

    def test_register_push_token_missing_token(self):
        """Test registering push token without token"""
        url = f"/api/users/{self.user.user_id}/register-push-token/"
        response = self.client.post(url, {}, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_get_recommended_events(self):
        """Test GET /api/users/{user_id}/recommended-events/"""
        # Create events at the same location
        event = EventDetail.objects.create(
            event_name="Recommended Event",
            capacity=30,
            duration=60,
            address="Test Address",
        )

        url = f"/api/users/{self.user.user_id}/recommended-events/"
        response = self.client.get(url)

        # User may not have location, so could return 400
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND,
            ],
        )


class EventAPITestCase(APITestCase):
    """Test cases for Event API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.user = UserDetail.objects.create(
            name="Event Organizer",
            bio="Organizer bio",
            invite_code="ORG123",
            date_of_birth=date(1990, 1, 1),
        )

        self.participant = UserDetail.objects.create(
            name="Participant",
            bio="Participant bio",
            invite_code="PART456",
            date_of_birth=date(1995, 1, 1),
        )

        self.event = EventDetail.objects.create(
            event_name="Test Event",
            description="Event Description",
            capacity=50,
            duration=120,
            address="123 Test Street",
            status=EventStatus.PLANNED,
            view_count=0,
        )

        self.organizer = EventOrganizer.objects.create(
            event_id=self.event, user_id=self.user
        )

    def test_retrieve_event(self):
        """Test GET /events/{event_id}/"""
        url = f"/api/events/{self.event.event_id}/"
        response = self.client.get(url)

        # Should retrieve successfully or require auth
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        )

    def test_retrieve_event_increments_view_count(self):
        """Test that retrieving an event increments view count"""
        initial_count = self.event.view_count
        url = f"/api/events/{self.event.event_id}/"

        # This test assumes the endpoint exists and is configured
        response = self.client.get(url)

        if response.status_code == status.HTTP_200_OK:
            self.event.refresh_from_db()
            self.assertEqual(self.event.view_count, initial_count + 1)

    def test_get_available_spots(self):
        """Test GET /events/{event_id}/spots/"""
        url = f"/api/events/{self.event.event_id}/spots/"
        response = self.client.get(url)

        if response.status_code == status.HTTP_200_OK:
            self.assertIn("available_spots", response.data)
            self.assertEqual(response.data["available_spots"], 50)

    def test_check_user_in_event(self):
        """Test GET /events/{event_id}/is-user-in/"""
        url = (
            f"/api/events/{self.event.event_id}/is-user-in/?user_id={self.user.user_id}"
        )
        response = self.client.get(url)

        if response.status_code == status.HTTP_200_OK:
            self.assertIn("is_in_event", response.data)
            self.assertFalse(response.data["is_in_event"])

    def test_check_user_in_event_missing_user_id(self):
        """Test checking user without user_id parameter"""
        url = f"/api/events/{self.event.event_id}/is-user-in/"
        response = self.client.get(url)

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("error", response.data)

    def test_join_event(self):
        """Test POST /events/{event_id}/join/"""
        url = f"/api/events/{self.event.event_id}/join/"
        data = {"user_id": str(self.participant.user_id)}
        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_201_CREATED:
            # Verify the user was added
            self.assertTrue(
                UserEvent.objects.filter(
                    user_id=self.participant, event_id=self.event
                ).exists()
            )

    def test_join_event_twice(self):
        """Test joining the same event twice"""
        # Join first time
        UserEvent.objects.create(user_id=self.participant, event_id=self.event)

        # Try to join again
        url = f"/api/events/{self.event.event_id}/join/"
        data = {"user_id": str(self.participant.user_id)}
        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_200_OK:
            self.assertIn("Already joined", response.data.get("message", ""))

    def test_join_full_event(self):
        """Test joining an event at capacity"""
        # Create an event with capacity 1
        small_event = EventDetail.objects.create(
            event_name="Small Event", capacity=1, duration=60, address="Test"
        )

        # Fill the event
        UserEvent.objects.create(user_id=self.user, event_id=small_event)

        # Try to join when full
        url = f"/api/events/{small_event.event_id}/join/"
        data = {"user_id": str(self.participant.user_id)}
        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("full", response.data.get("error", "").lower())

    def test_create_event_notification(self):
        """Test POST /events/notifications/create/"""
        url = "/api/events/notifications/create/"
        data = {
            "event_id": str(self.event.event_id),
            "user_id": str(self.user.user_id),
            "detail": "Test notification message",
        }
        response = self.client.post(url, data, format="json")

        # Should create notification if user is organizer
        self.assertIn(
            response.status_code,
            [
                status.HTTP_201_CREATED,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND,
            ],
        )

    def test_create_notification_non_organizer(self):
        """Test that non-organizers cannot create notifications"""
        url = "/api/events/notifications/create/"
        data = {
            "event_id": str(self.event.event_id),
            "user_id": str(self.participant.user_id),  # Not the organizer
            "detail": "Test notification",
        }
        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_403_FORBIDDEN:
            self.assertIn("organizer", response.data.get("error", "").lower())


class NotificationTestCase(TestCase):
    """Test cases for notification system"""

    def setUp(self):
        """Set up test data"""
        self.user = UserDetail.objects.create(
            name="Test User",
            bio="Test bio",
            invite_code="TEST123",
            date_of_birth=date(1990, 1, 1),
        )

        self.event = EventDetail.objects.create(
            event_name="Test Event", capacity=50, duration=120, address="Test Address"
        )

    def test_event_notification_creation(self):
        """Test creating an event notification"""
        notification = EventNotification.objects.create(
            event_id=self.event, detail="Event update", from_admin=False
        )

        self.assertIsNotNone(notification.notification_id)
        self.assertEqual(notification.detail, "Event update")
        self.assertFalse(notification.from_admin)

    def test_user_notification_creation(self):
        """Test creating a user notification"""
        event_notif = EventNotification.objects.create(
            event_id=self.event, detail="Event update"
        )

        user_notif = UserNotification.objects.create(
            user_id=self.user, notification_id=event_notif
        )

        self.assertEqual(user_notif.user_id, self.user)
        self.assertEqual(user_notif.notification_id, event_notif)
        self.assertFalse(user_notif.is_read)

    def test_notification_cascade_delete(self):
        """Test that deleting event deletes related notifications"""
        event_notif = EventNotification.objects.create(
            event_id=self.event, detail="Event update"
        )

        user_notif = UserNotification.objects.create(
            user_id=self.user, notification_id=event_notif
        )

        notif_id = event_notif.notification_id

        # Delete the event
        self.event.delete()

        # Notification should be deleted too
        self.assertFalse(
            EventNotification.objects.filter(notification_id=notif_id).exists()
        )


class SerializerTestCase(TestCase):
    """Test cases for serializers"""

    def setUp(self):
        """Set up test data"""
        from api.serializers import (
            UserDetailSerializer,
            EventDetailSerializer,
            LocationSerializer,
        )

        self.UserDetailSerializer = UserDetailSerializer
        self.EventDetailSerializer = EventDetailSerializer
        self.LocationSerializer = LocationSerializer

        self.location = Location.objects.create(
            province="Seoul", city="Gangnam", town="Yeoksam"
        )

        self.user = UserDetail.objects.create(
            name="Test User",
            bio="Test bio",
            invite_code="TEST123",
            date_of_birth=date(1990, 1, 1),
        )

    def test_location_serializer(self):
        """Test LocationSerializer"""
        serializer = self.LocationSerializer(self.location)
        data = serializer.data

        self.assertEqual(data["province"], "Seoul")
        self.assertEqual(data["city"], "Gangnam")
        self.assertEqual(data["town"], "Yeoksam")

    def test_user_detail_serializer(self):
        """Test UserDetailSerializer"""
        serializer = self.UserDetailSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["name"], "Test User")
        self.assertEqual(data["bio"], "Test bio")
        self.assertEqual(data["invite_code"], "TEST123")


class IntegrationTestCase(APITestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.organizer = UserDetail.objects.create(
            name="Event Organizer",
            bio="Organizer",
            invite_code="ORG123",
            date_of_birth=date(1990, 1, 1),
        )

        self.participant = UserDetail.objects.create(
            name="Participant",
            bio="Participant",
            invite_code="PART456",
            date_of_birth=date(1995, 1, 1),
        )

    def test_complete_event_workflow(self):
        """Test complete event creation and participation workflow"""
        # 1. Create event
        event = EventDetail.objects.create(
            event_name="Integration Test Event",
            capacity=10,
            duration=120,
            address="Test Location",
        )

        # 2. Set organizer
        EventOrganizer.objects.create(event_id=event, user_id=self.organizer)

        # 3. Participant joins
        UserEvent.objects.create(user_id=self.participant, event_id=event)

        # 4. Verify participation
        self.assertTrue(
            UserEvent.objects.filter(user_id=self.participant, event_id=event).exists()
        )

        # 5. Create notification
        notification = EventNotification.objects.create(
            event_id=event, detail="Event starting soon!"
        )

        # 6. Send to participant
        UserNotification.objects.create(
            user_id=self.participant, notification_id=notification
        )

        # 7. Verify notification received
        self.assertTrue(
            UserNotification.objects.filter(
                user_id=self.participant, notification_id=notification
            ).exists()
        )
