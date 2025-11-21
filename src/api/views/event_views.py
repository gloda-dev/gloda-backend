from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from api.models.event import (
    UserDetail,
    EventDetail,
    UserEvent,
    EventOrganizer,
    UserNotification,
)
from rest_framework.response import Response
from api.serializers import EventDetailSerializer, EventNotificationSerializer
from api.models.notification import EventNotification


class EventViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        """GET /events/{event_id}/"""
        try:
            event = EventDetail.objects.get(pk=pk)
            serializer = EventDetailSerializer(event)
            return Response(serializer.data)

        except EventDetail.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

    @action(detail=True, methods=["get"])
    def spots(self, request, pk=None):
        """GET /events/{event_id}/spots/"""
        try:
            event = EventDetail.objects.get(pk=pk)

            participants_count = UserEvent.objects.filter(event_id=pk).count()
            spots = event.capacity - participants_count

            return Response({"available_spots": spots})

        except EventDetail.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

    @action(detail=True, methods=["get"])
    def is_user_in(self, request, pk=None):
        """GET /events/{event_id}/is-user-in/?user_id=UUID"""
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)

        exists = UserEvent.objects.filter(user_id=user_id, event_id=pk).exists()

        return Response({"is_in_event": exists})

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        """POST /events/{event_id}/join/ (body: {user_id})"""
        user_id = request.data.get("user_id")  # TODO: frontend return user_id in body?
        if not user_id:
            return Response({"error": "user_id required"}, status=400)

        try:
            user = UserDetail.objects.get(pk=user_id)
            event = EventDetail.objects.get(pk=pk)

            if UserEvent.objects.filter(user=user, event=event).exists():
                return Response({"message": "Already joined"})

            if event.participants.count() >= event.capacity:
                return Response({"error": "Event is full"}, status=400)

            UserEvent.objects.create(user=user, event=event)
            return Response({"message": "Joined successfully"}, status=201)

        except (UserDetail.DoesNotExist, EventDetail.DoesNotExist):
            return Response({"error": "User or Event not found"}, status=404)

    @action(detail=True, methods=["post"])
    def create_event(self, request):
        """POST /events/create/"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)

        try:
            user = UserDetail.objects.get(pk=user_id)
            serializer = EventDetailSerializer(data=request.data)
            if serializer.is_valid():
                event = serializer.save(organizer=user)
                return Response(EventDetailSerializer(event).data, status=201)
            else:
                return Response(serializer.errors, status=400)
        except UserDetail.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(detail=True, methods=["get"])
    def notificaions(self, request, pk=None):
        """GET /events/{event_id}/notifications/"""
        try:
            event = EventNotification.objects.get(pk=pk)
            serializer = EventNotificationSerializer(event)
            return Response(serializer.data)
        except EventNotification.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

    @action(detail=False, methods=["post"])
    def create_notification(self, request):
        """POST /events/notifications/create/ (body: {event_id, user_id, detail})"""
        try:
            event = EventDetail.objects.get(pk=request.data.get("event_id"))
            organizer = EventOrganizer.objects.get(event_id=event)

            if organizer.user_id.pk != request.data.get("user_id"):
                return Response(
                    {"error": "Only organizer can create notification"}, status=403
                )
            
            notification = EventNotification.objects.create(
                event_id=event, detail=request.data.get("detail", "")
            )

            participants = UserEvent.objects.filter(event_id=event)

            for participant in participants:
                UserNotification.objects.create(
                    user_id=participant.user_id,
                    notification_id=notification.notification_id,
                )

            return Response(
                {
                    "notification_id": notification.notification_id,
                    "event_id": notification.event_id.event_id,
                    "detail": notification.detail,
                    "time_created": notification.time_created,
                },
                status=201,
            )
        except EventDetail.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
