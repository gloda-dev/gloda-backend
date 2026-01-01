from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.user_views import UserDetailViewSet
from api.views.event_views import EventViewSet
from api.views.auth_views import kakao_redirect

router = DefaultRouter()
router.register(r"users", UserDetailViewSet, basename="users")
router.register(r"events", EventViewSet, basename="events")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/kakao/callback", kakao_redirect),
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
