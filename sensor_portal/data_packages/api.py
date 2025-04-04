from rest_framework import routers

from .viewsets import DataPackageViewSet

router = routers.DefaultRouter()
router.register(r"datapackage", DataPackageViewSet, basename='datapackage')
