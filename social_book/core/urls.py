from django import views
from django.urls import path
from . import views

urlpatterns = [
    # home url, goes to view -> index
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup')
]
