import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import GameResult


@csrf_exempt
def submit_game_result(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = User.objects.get(username=data["username"])
        GameResult.objects.create(
            player=user, role=data["role"], score=data["score"], outcome=data["outcome"]
        )
        return JsonResponse({"status": "success"}, status=200)
