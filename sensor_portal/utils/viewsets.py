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


class AddOwnerViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CheckFormViewSet(ModelViewSet):
    def get_serializer_context(self):
        context = super(CheckFormViewSet, self).get_serializer_context()

        context.update(
            {'form': 'multipart/form-data' in self.request.content_type})
        return context
