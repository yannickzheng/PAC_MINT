from django.urls import path
from django.conf import settings
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

# URLs de test seulement en mode DEBUG
if settings.DEBUG:
    from .views.test_views import test_404_view
    urlpatterns += [
        path('test-404/', test_404_view, name='test_404'),
    ]
