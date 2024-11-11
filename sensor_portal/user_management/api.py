
from rest_framework import routers
from user_management.viewsets import UserViewSet

router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename='user')
