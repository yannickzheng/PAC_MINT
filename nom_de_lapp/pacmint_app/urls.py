from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import CustomLoginView, home, register_player

urlpatterns = [
    path('', home, name='home'),
    path('inscription/', register_player, name='register'),
    path('connexion/', CustomLoginView.as_view(), name='login'),  # <--- Ici
]
