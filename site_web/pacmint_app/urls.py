from django.urls import path
from . import views

app_name = 'pacmint_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.register_player, name='register'),
    path('login/', views.home, name='login'),
    path('register/', views.register_player, name='register_player'),
    path('api/submit-score/', views.submit_score, name='submit_score'),
    path('scores/', views.score_list, name='score_list'),
]
