from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profil_view(request):
    return render(request, 'pacmint_app/profil.html', {'user': request.user})