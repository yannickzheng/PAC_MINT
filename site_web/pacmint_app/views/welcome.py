from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def welcome_player(request):
    return render(request, 'welcome.html', {'username': request.user.username})