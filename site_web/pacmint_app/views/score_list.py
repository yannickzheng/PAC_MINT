from ..models import Score
from django.shortcuts import render
from django.contrib.auth.models import User

def score_list(request):
    scores = Score.objects.all().order_by('-value')[:20]  # Top 20
    return render(request, 'scores.html', {'scores': scores})
