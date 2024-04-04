from rest_framework import routers
from .viewsets import *

router = routers.DefaultRouter()
router.register(r"deployment", DeploymentViewSet, basename='deployment')
router.register(r"project", ProjectViewSet, basename='project')
router.register(r"device", DeviceViewSet, basename='device')
router.register(r"datafile", DataFileViewSet, basename='datafile')
urlpatterns = router.urls
