from camtrap_dp_export.api import router as camtrap_dp_router
from data_handlers.api import router as data_handlers_router
from data_models.api import router as data_models_router
from data_packages.api import router as data_package_router
from external_storage_import.api import router as external_storage_router
from observation_editor.api import router as observation_editor_router
from rest_framework import routers
from user_management.api import router as user_management_router

router = routers.DefaultRouter()
router.registry.extend(data_models_router.registry)
router.registry.extend(user_management_router.registry)
router.registry.extend(observation_editor_router.registry)
router.registry.extend(camtrap_dp_router.registry)
router.registry.extend(data_package_router.registry)
router.registry.extend(data_handlers_router.registry)
router.registry.extend(external_storage_router.registry)
urlpatterns = router.urls
