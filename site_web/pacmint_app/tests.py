from django.test import TestCase
from django.contrib.auth.models import User
import json


class GameResultAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alban", password="test")

    def test_submit_game_result(self):
        response = self.client.post(
            "/api/submit-result/",
            data=json.dumps(
                {"username": "alban", "role": "pacman", "score": 9000, "outcome": "win"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
