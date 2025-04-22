from django.core.exceptions import ObjectDoesNotExist
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
