from django.contrib.auth.hashers import check_password

from ..models import Player


class PlayerAuthBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            player = Player.objects.get(username=username)
            if check_password(password, player.password):
                return player
            return None
        except Player.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Player.objects.get(pk=user_id)
        except Player.DoesNotExist:
            return None
