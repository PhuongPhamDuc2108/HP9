from django.urls import path
from . import views

urlpatterns = [
    path('', views.introduction_view, name='introduction'),
]