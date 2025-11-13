from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from api.models.event import UserDetail, EventDetail, UserEvent
from rest_framework.response import Response
from api.serializers import EventDetailSerializer


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
        user_id = request.data.get("user_id")
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
