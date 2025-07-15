from django.contrib import messages
from django.shortcuts import redirect, render

from ..forms import PlayerRegistrationForm


def register_player(request):
    if request.method == "POST":
        form = PlayerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Inscription réussie ! Vous pouvez maintenant vous connecter."
            )
            return redirect("pacmint_app:login")
        else:
            messages.error(
                request,
                "Erreur lors de l'inscription. Vérifiez les informations fournies.",
            )
    else:
        form = PlayerRegistrationForm()
    return render(request, "register.html", {"formulaire": form})
