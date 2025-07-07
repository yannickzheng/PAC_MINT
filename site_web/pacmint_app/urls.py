from django.urls import path
from django.conf import settings
from . import views
from .views.api import submit_game_result

app_name = 'pacmint_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_player, name='register'),
    path('welcome/', views.welcome_player, name='welcome'),
    path('api/submit-score/', views.submit_score, name='submit_score'),
    path('scores/', views.score_list, name='score_list'),
    path('login/', views.login_player, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('api/submit-result/', submit_game_result, name='submit_result'), ]




# URLs de test seulement en mode DEBUG
if settings.DEBUG:
    from .views.test_views import test_404_view, test_500_view
    urlpatterns += [
        path('test-404/', test_404_view, name='test_404'),
        path('test-500/', test_500_view, name='test_500')

    ]
