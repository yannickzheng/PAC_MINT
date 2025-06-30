from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import Score

@login_required
def profile_view(request):
    user_scores = Score.objects.filter(player=request.user)
    total_games = user_scores.count()
    total_wins = user_scores.filter(result='win').count()
    total_losses = user_scores.filter(result='loss').count()
    total_score = sum(score.value for score in user_scores)

    win_ratio = f"{(total_wins / total_games * 100):.1f}%" if total_games > 0 else "N/A"

    context = {
        'total_games': total_games,
        'total_wins': total_wins,
        'total_losses': total_losses,
        'win_ratio': win_ratio,
        'total_score': total_score
    }
    return render(request, 'profile.html', context)
