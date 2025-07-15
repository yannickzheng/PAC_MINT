from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def welcome_player(request):
    return render(request, "welcome.html", {"username": request.user.username})
