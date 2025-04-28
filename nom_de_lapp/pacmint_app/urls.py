from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.register_player, name='register'),
    path('connexion/', auth_views.LoginView.as_view(), name='login'),
]
