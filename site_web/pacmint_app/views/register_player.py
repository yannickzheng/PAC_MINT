from django.shortcuts import render, redirect
from ..forms import PlayerRegistrationForm
from django.contrib import messages
from ..models import Player
from django.contrib.auth.hashers import make_password

def register_player(request):
    if request.method == 'POST':
        form = PlayerRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas, veuillez vérifier votre saisie.")
                return redirect('register')
            player = Player(username=username, email=email, password=make_password(password))
            player.save()
            messages.success(request, "Votre inscription a été réussie ! Vous pouvez maintenant vous connecter.")
            return redirect('login')  #  l'URL de la page de connexion

    else:
        form = PlayerRegistrationForm()
    return render(
        request,
        'register.html',
        {'formulaire': form})