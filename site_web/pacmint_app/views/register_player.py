from django.shortcuts import render, redirect
from ..forms import PlayerRegistrationForm
from django.contrib import messages
from ..models import Player
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

def register_player(request):
    if request.method == 'POST':
        form = PlayerRegistrationForm(request.POST)
        print("Données POST :", request.POST)  # Débogage : affiche les données envoyées
        if form.is_valid():
            print("Formulaire valide")  # Débogage
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas, veuillez vérifier votre saisie.")
                return redirect('pacmint_app:register')
            try:
                player = Player(username=username, email=email, password=make_password(password))
                player.save()
                messages.success(request, "Votre inscription a été réussie ! Vous pouvez maintenant vous connecter.")
                return redirect('pacmint_app:login')
            except IntegrityError:
                messages.error(request, "Ce nom d'utilisateur ou cet email est déjà utilisé.")
                return redirect('pacmint_app:register')
        else:
            print("Formulaire non valide :", form.errors)  # Débogage : affiche les erreurs
            messages.error(request, "Erreur dans le formulaire. Veuillez vérifier vos informations.")
    else:
        form = PlayerRegistrationForm()
    return render(request, 'register.html', {'formulaire': form})