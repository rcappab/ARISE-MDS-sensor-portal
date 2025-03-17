from rest_framework import routers

from .viewsets import SequenceViewsetCTDP

router = routers.DefaultRouter()
router.register(r"sequence", SequenceViewsetCTDP, basename='sequence')
