from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render

from ..models import Friend, GameResult


@login_required
def friend_profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    is_friend = Friend.objects.filter(
        player=request.user, friend=target_user, status="accepted"
    ).exists()

    if not is_friend:
        return render(request, "403.html", status=403)

    results = GameResult.objects.filter(player=target_user)

    total_games = results.count()
    total_wins = results.filter(outcome="win").count()
    total_losses = results.filter(outcome="lose").count()
    total_score = sum(r.score for r in results)
    win_ratio = f"{(total_wins / total_games * 100):.1f}%" if total_games > 0 else "N/A"

    context = {
        "friend": target_user,
        "total_games": total_games,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "win_ratio": win_ratio,
        "total_score": total_score,
    }

    return render(request, "friend_profile.html", context)
