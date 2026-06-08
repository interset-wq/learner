from django.urls import include, path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("user/<str:username>/", views.public_profile, name="public_profile"),
]
