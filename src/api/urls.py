from rest_framework.routers import DefaultRouter
from api.views import UserDetailViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"user-details", UserDetailViewSet, basename="user-detail")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
