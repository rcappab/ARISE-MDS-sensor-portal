from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filtersets import UserFilter
from .models import User
from .serializers import UserProfileSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'head']
    filterset_class = UserFilter
    serializer_class = UserSerializer
    search_fields = ['email',
                     'username', 'first_name', 'last_name', 'organisation']

    def get_permissions(self):

        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    queryset = User.objects.all().distinct()


class UserProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head']
    filterset_class = UserFilter
    serializer_class = UserProfileSerializer
    search_fields = ['email',
                     'username', 'first_name', 'last_name', 'organisation']
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().distinct()

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Method 'GET' not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        user_obj = get_object_or_404(pk=pk, klass=self.queryset)

        if not request.user == user_obj and not request.user.is_staff:
            return Response({"detail": " You do not have permission to view this item."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().retrieve(request, *args, **kwargs)
