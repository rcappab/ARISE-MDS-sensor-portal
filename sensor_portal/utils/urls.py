from django.urls import path

from .views import AllTimezoneView

urlpatterns = [
    path('timezones', AllTimezoneView, name='timezones'),
]
