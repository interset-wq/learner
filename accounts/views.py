from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm


def register(request):
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect("/")
    context = {"form": form}
    return render(request, "registration/register.html", context)


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    context = {"form": form}
    return render(request, "registration/profile.html", context)


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    from learning_logs.models import Topic

    public_topics = Topic.objects.filter(owner=profile_user, is_public=True).order_by(
        "-date_added"
    )[:20]
    context = {"profile_user": profile_user, "public_topics": public_topics}
    return render(request, "registration/public_profile.html", context)
