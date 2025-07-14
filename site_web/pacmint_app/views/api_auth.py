from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({
                "status": "ok",
                "username": user.username,
                "user_id": user.id  # ✅ Ajouté ici
            })
        else:
            return JsonResponse({"status": "fail", "error": "Identifiants invalides"}, status=401)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
