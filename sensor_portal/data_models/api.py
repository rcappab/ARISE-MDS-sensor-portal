from rest_framework import routers
from .viewsets import *

router = routers.DefaultRouter()
router.register(r"deployment", DeploymentViewset, basename='deployment')
router.register(r"project", ProjectViewset, basename='project')
router.register(r"device", DeviceViewset, basename='device')
router.register(r"datafile", DataFileViewset, basename='datafile')
urlpatterns = router.urls
