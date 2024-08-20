from data_models.api import router as data_models_router
from rest_framework import routers

router = routers.DefaultRouter()
router.registry.extend(data_models_router.registry)
urlpatterns = router.urls
