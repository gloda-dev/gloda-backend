from django.shortcuts import render
from rest_framework import viewsets
from api.models.event import UserDetail
from api.serializers import UserDetailSerializer


class UserDetailViewSet(viewsets.ModelViewSet):
    queryset = UserDetail.objects.all()
    serializer_class = UserDetailSerializer
