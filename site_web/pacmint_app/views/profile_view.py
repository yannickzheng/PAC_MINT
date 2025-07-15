from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import GameResult


@login_required
def profile_view(request):
    user_results = GameResult.objects.select_related("player").filter(
        player=request.user
    )

    total_games = user_results.count()
    total_wins = user_results.filter(outcome="win").count()
    total_losses = user_results.filter(outcome="lose").count()
    total_score = sum(result.score for result in user_results)

    win_ratio = f"{(total_wins / total_games * 100):.1f}%" if total_games > 0 else "N/A"

    context = {
        "total_games": total_games,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "win_ratio": win_ratio,
        "total_score": total_score,
    }

    return render(request, "profile.html", context)
