from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from api.models.event import UserDetail
from api.serializers import UserDetailSerializer
