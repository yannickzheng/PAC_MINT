from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from ..forms import PlayerLoginForm


def login_player(request):
    if request.method == 'POST':
        form = PlayerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('pacmint_app:welcome')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else :
            messages.error(request,"Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PlayerLoginForm()
    return render(request, "login.html", {'formulaire': form})