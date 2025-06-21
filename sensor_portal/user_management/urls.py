from django.urls import include, path

from .views import MyTokenObtainPairView, MyTokenRefreshView

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset'))
]
