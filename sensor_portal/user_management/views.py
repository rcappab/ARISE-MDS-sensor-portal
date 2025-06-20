from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .serializers import MyTokenObtainPairSerializer


@extend_schema(exclude=True)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(exclude=True)
class MyTokenRefreshView(TokenRefreshView):
    pass
