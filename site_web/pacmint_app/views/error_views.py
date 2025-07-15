from django.http import HttpResponseNotFound
from django.shortcuts import render


def custom_404_view(request, exception):
    """
    Vue personnalisée pour les erreurs 404.
    Cette vue est appelée automatiquement par Django quand une page n'est pas trouvée.
    """
    return render(request, "404.html", status=404)


def custom_500_view(request):
    """
    Vue personnalisée pour les erreurs 500.
    Cette vue est appelée automatiquement par Django en cas d'erreur serveur interne.
    """
    return render(request, "500.html", status=500)
