from rest_framework import routers

from .viewsets import DataStorageInputViewSet

router = routers.DefaultRouter()
router.register(r"datastorageinput", DataStorageInputViewSet,
                basename='datastorageinput')
