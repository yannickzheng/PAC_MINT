from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from ..models import Friend
from django.contrib import messages


@login_required
def send_friend_request(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Friend.objects.get_or_create(
            player=request.user, friend=target, status="pending"
        )
    return redirect("pacmint_app:friends")


@login_required
def accept_friend_request(request, username):
    sender = get_object_or_404(User, username=username)
    try:
        request_obj = Friend.objects.get(
            player=sender, friend=request.user, status="pending"
        )
        request_obj.status = "accepted"
        request_obj.save()
        Friend.objects.get_or_create(
            player=request.user, friend=sender, status="accepted"
        )
    except Friend.DoesNotExist:
        pass
    return redirect("pacmint_app:friends")


@login_required
def friends_view(request):
    friends = Friend.objects.select_related("friend").filter(
        player=request.user, status="accepted"
    )
    incoming = Friend.objects.select_related("player").filter(
        friend=request.user, status="pending"
    )

    suggestions = User.objects.exclude(id=request.user.id).exclude(
        id__in=Friend.objects.filter(player=request.user).values_list(
            "friend_id", flat=True
        )
    )

    return render(
        request,
        "friends.html",
        {
            "friends": friends,
            "incoming_requests": incoming,
            "suggestions": suggestions,
        },
    )


@login_required
def add_friend(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if username == request.user.username:
            messages.error(request, "Vous ne pouvez pas vous ajouter vous-même.")
            return redirect("pacmint_app:friends")

        try:
            friend_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Aucun utilisateur avec ce nom.")
            return redirect("pacmint_app:friends")

        already_requested = Friend.objects.filter(
            player=request.user, friend=friend_user
        ).exists()
        already_received = Friend.objects.filter(
            player=friend_user, friend=request.user
        ).exists()

        if already_requested or already_received:
            messages.info(request, "Une relation existe déjà avec cet utilisateur.")
        else:
            Friend.objects.create(
                player=request.user, friend=friend_user, status="pending"
            )
            messages.success(request, f"Demande envoyée à {username}.")

    return redirect("pacmint_app:friends")
