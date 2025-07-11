from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from ..models import Friend

@login_required
def send_friend_request(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Friend.objects.get_or_create(player=request.user, friend=target, status="pending")
    return redirect("pacmint_app:friends")

@login_required
def accept_friend_request(request, username):
    sender = get_object_or_404(User, username=username)
    try:
        request_obj = Friend.objects.get(player=sender, friend=request.user, status="pending")
        request_obj.status = "accepted"
        request_obj.save()
        # Ajouter la relation inverse
        Friend.objects.get_or_create(player=request.user, friend=sender, status="accepted")
    except Friend.DoesNotExist:
        pass
    return redirect("pacmint_app:friends")

@login_required
def friends_view(request):
    friends = Friend.objects.filter(player=request.user, status="accepted")
    incoming = Friend.objects.filter(friend=request.user, status="pending")
    suggestions = User.objects.exclude(id=request.user.id).exclude(
        id__in=Friend.objects.filter(player=request.user).values_list('friend_id', flat=True)
    )
    return render(request, "friends.html", {
        "friends": friends,
        "incoming_requests": incoming,
        "suggestions": suggestions,
    })
