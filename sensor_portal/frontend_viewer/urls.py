from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="viewer_index"),
]
