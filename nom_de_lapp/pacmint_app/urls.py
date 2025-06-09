from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import CustomLoginView, home, register_player, score_list,submit_score

urlpatterns = [
    path('', home, name='home'),
    path('inscription/', register_player, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('api/submit-score/', submit_score, name='submit_score'),
    path('scores/', score_list, name='score_list'),
]
