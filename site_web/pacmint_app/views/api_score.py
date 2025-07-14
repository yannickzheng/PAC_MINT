from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
import traceback
from ..models import GameResult

@csrf_exempt
def api_submit_score(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("✅ Données reçues :", data)

            user_id = data.get("user_id")
            role = data.get("role")
            score = data.get("score")
            outcome = data.get("outcome")

            user = User.objects.get(id=user_id)

            GameResult.objects.create(
                player=user,
                role=role,
                score=score,
                outcome=outcome
            )

            print("✅ Score enregistré avec succès")
            return JsonResponse({"status": "success"})

        except Exception as e:
            print("❌ Erreur lors de l'enregistrement du score :", str(e))
            traceback.print_exc()
            return JsonResponse(
                {"status": "fail", "message": "Erreur interne"},
                status=500
            )

    return JsonResponse({"error": "POST method required"}, status=405)
