from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.index, name="index"),
    path("questions/", views.QuestionListView.as_view(), name="questions"),
    path("questions/<int:pk>/", views.QuestionDetailView.as_view(), name="detail"),
    path(
        "questions/<int:pk>/results/", views.ResultsDetailView.as_view(), name="results"
    ),
    path("questions/<int:question_id>/vote/", views.vote, name="vote"),
]
