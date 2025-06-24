import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from ..models import Score

@csrf_exempt
def submit_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            score_value = data.get('score')

            user = User.objects.get(username=username)
            Score.objects.create(player=user, value=score_value)

            return JsonResponse({'status': 'ok', 'message': 'Score enregistré'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
