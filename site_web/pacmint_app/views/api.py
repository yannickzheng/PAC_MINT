from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from ..models import GameResult

@csrf_exempt
def submit_game_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username')
            role = data.get('role')
            score = data.get('score')
            outcome = data.get('outcome')

            user = User.objects.get(username=username)

            GameResult.objects.create(
                player=user,
                role=role,
                score=score,
                outcome=outcome
            )
            return JsonResponse({'status': 'success'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)
