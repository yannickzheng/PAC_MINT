
from django.shortcuts import render, redirect
from .forms import PlayerRegistrationForm
from django.contrib import messages
from .models import Player
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.http import HttpResponse

def register_player(request):
    if request.method == 'POST':
        form = PlayerRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Créer un nouveau joueur et le sauvegarder
            player = Player(username=username, email=email, password=make_password(password))
            player.save()

            messages.success(request, "Votre inscription a été réussie ! Vous pouvez maintenant vous connecter.")
            return redirect('login')  #  l'URL de la page de connexion
    else:
        form = PlayerRegistrationForm()

    return render(request, 'register.html', {'form': form})


def home(request):
    return render(request, 'home.html')


from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # ➔ au lieu de 'registration/login.html'

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Score

@csrf_exempt
def submit_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            score_value = data.get('score')

            user = User.objects.get(username=username)
            Score.objects.create(player=user, value=score_value)

            return JsonResponse({'status': 'ok', 'message': 'Score enregistré'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

from .models import Score
from django.contrib.auth.models import User

def score_list(request):
    scores = Score.objects.all().order_by('-value')[:20]  # Top 20
    return render(request, 'scores.html', {'scores': scores})


# Create your views here.
