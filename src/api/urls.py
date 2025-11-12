from rest_framework.routers import DefaultRouter
from api.views import UserDetailViewSet

router = DefaultRouter()
router.register(r"user-details", UserDetailViewSet, basename="user-detail")

urlpatterns = router.urls
