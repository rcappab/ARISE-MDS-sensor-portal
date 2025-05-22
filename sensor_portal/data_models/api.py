from rest_framework import routers

from .viewsets import (DataFileViewSet, DataTypeViewSet, DeploymentViewSet,
                       DeviceModelViewSet, DeviceViewSet, GenericJobViewSet,
                       ProjectViewSet, SiteViewSet)

router = routers.DefaultRouter()
router.register(r"deployment", DeploymentViewSet, basename='deployment')
router.register(r"project", ProjectViewSet, basename='project')
router.register(r"device", DeviceViewSet, basename='device')
router.register(r"datafile", DataFileViewSet, basename='datafile')
router.register(r"site", SiteViewSet, basename='site')
router.register(r"datatype", DataTypeViewSet, basename='datatype')
router.register(r"devicemodel", DeviceModelViewSet, basename='devicemodel')
router.register(r"genericjob", GenericJobViewSet, basename='genericjob')
