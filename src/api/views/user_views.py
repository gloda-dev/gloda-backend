from django.shortcuts import render
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from api.models.event import UserDetail, EventDetail
from api.models.notification import UserNotification
from api.serializers import (
    UserDetailSerializer,
    SimpleUserDetailSerializer,
    EventDetailSerializer,
    CreateUserSerializer,
)
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class UserDetailViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, pk=None):
        """GET /users/{user_id}/"""
        try:
            user = UserDetail.objects.get(pk=pk)
            serializer = SimpleUserDetailSerializer(user)
            return Response(serializer.data)

        except UserDetail.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def myinfo(self, request, pk=None):
        """GET /users/{user_id}/myinfo/"""
        try:
            user = UserDetail.objects.get(pk=pk)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)

        except UserDetail.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(detail=True, methods=["get"])
    def recommended_events(self, request, pk=None):
        """GET /users/{user_id}/recommended-events/"""
        try:
            user = UserDetail.objects.get(pk=pk)
            if not user.location:
                return Response({"error": "User has no location"}, status=400)

            events = EventDetail.objects.filter(location=user.location).exclude(
                participants=user
            )

            serializer = EventDetailSerializer(events, many=True)
            return Response(serializer.data)

        except UserDetail.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(detail=False, methods=["post"])
    def create_user(self, request):
        """POST /users/create/"""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserDetailSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["get"])
    def notifications(self, request, pk=None):
        """GET /users/{user_id}/notifications/"""
        try:
            user = UserNotification.objects.get(pk=pk)
            notifications = user.notifications.all().order_by("-time_created")
            notifications_data = [
                {
                    "notification_id": n.notification_id,
                    "detail": n.notification_id.detail,
                    "time_created": n.notification_id.time_created,
                    "is_read": n.is_read,
                }
                for n in notifications
            ]
            return Response(notifications_data)

        except UserDetail.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
