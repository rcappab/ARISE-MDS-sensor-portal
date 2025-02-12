from django.conf import settings
from rest_framework.viewsets import ModelViewSet


class OptionalPaginationViewSet(ModelViewSet):
    """By default, paginate_queryset returns None when no paginator is set. This extends
    it to also return None if no 'page' query param is set"""

    def paginate_queryset(self, queryset):
        if self.paginator \
                and self.request.query_params.get(self.paginator.page_query_param, None) is None \
                and queryset.count() < settings.REST_FRAMEWORK['MAX_PAGE_SIZE']:
            return None
        return super().paginate_queryset(queryset)
