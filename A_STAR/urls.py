from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    path('', views.home,name='home'),
    path('result', views.result, name='result'),
    path('cities', views.add_cities, name='cities'),
    ]