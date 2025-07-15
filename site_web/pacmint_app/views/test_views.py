from django.http import HttpResponse
from django.shortcuts import render


def test_404_view(request):
    """
    Vue de test pour afficher la page 404 personnalisée.
    À utiliser uniquement en développement.
    """
    # Rendre directement le template 404 avec le bon status code
    return render(request, "404.html", status=404)


def test_500_view(request):
    """ "
    Vue de test pour afficher la page 500 personnalisée
    """
    return render(request, "500.html")
