from django.urls import path
from . import views

app_name = 'pacmint_app'

urlpatterns = [
    path('home', views.home, name='home'),
    path('inscription/', views.register_player, name='register'),
    path('api/submit-score/', views.submit_score, name='submit_score'),
    path('scores/', views.score_list, name='score_list'),
]
