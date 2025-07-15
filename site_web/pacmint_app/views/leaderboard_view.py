from django.db.models import Sum
from django.shortcuts import render

from ..models import GameResult


def leaderboard_view(request):
    leaderboard = (
        GameResult.objects.select_related("player")  # évite N requêtes
        .values("player__username")
        .annotate(total_score=Sum("score"))
        .order_by("-total_score")[:10]
    )
    return render(request, "leaderboard.html", {"leaderboard": leaderboard})
