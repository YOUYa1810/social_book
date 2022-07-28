from django import views
from django.urls import path
from . import views

urlpatterns = [
    # home url, goes to view -> index
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout')

]
