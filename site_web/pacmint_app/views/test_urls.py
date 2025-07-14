# views/test_urls.py
from django.http import JsonResponse
from django.urls import get_resolver

def list_urls(request):
    resolver = get_resolver()
    urls = [str(p.pattern) for p in resolver.url_patterns]
    return JsonResponse({"urls": urls})
