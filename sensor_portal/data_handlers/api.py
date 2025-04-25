from rest_framework import routers

from .viewsets import DataHandlerViewSet

router = routers.DefaultRouter()
router.register(r"datahandler", DataHandlerViewSet, basename='datahandler')
