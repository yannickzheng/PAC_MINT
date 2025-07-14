from .home import home
from .register_player import register_player
from .welcome import welcome_player
from .login_player import login_player
from .profile_view import profile_view
from .logout_player import logout_view
from .leaderboard_view import leaderboard_view
from .friends import (
    friends_view,
    send_friend_request,
    accept_friend_request,
    add_friend,
)
from .friend_profile_view import friend_profile_view
from .api_auth import api_login
from .api_score import api_submit_score
from .test_urls import list_urls
