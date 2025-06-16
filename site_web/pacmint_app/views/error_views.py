from django.shortcuts import render
from django.http import HttpResponseNotFound


def custom_404_view(request, exception):
    """
    Vue personnalisée pour les erreurs 404.
    Cette vue est appelée automatiquement par Django quand une page n'est pas trouvée.
    """
    return render(request, '404.html', status=404)
