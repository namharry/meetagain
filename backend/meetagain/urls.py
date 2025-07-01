from django.urls import path
from . import views

app_name = 'meetagain'

urlpatterns = [
    path('', views.register_lost_item, name='register'),
    path('register/', views.register_lost_item, name='register'),
]