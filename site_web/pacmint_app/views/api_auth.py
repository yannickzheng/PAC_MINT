from django.contrib.auth import authenticate
from django.http import JsonResponse
import json

def api_login(request):
    if request.method != "POST":
        return JsonResponse({"status": "fail", "error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except json.JSONDecodeError:
        return JsonResponse({"status": "fail", "error": "Requête invalide"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        return JsonResponse({"status": "ok", "username": user.username})
    else:
        return JsonResponse({"status": "fail", "error": "Identifiants invalides"}, status=401)
