from django.urls import path

from . import views

app_name = "learning_logs"

urlpatterns = [
    path("", views.index, name="index"),
    path("topics/", views.TopicListView.as_view(), name="topics"),
    path("explore/", views.PublicTopicListView.as_view(), name="public_topics"),
    path("topics/<int:topic_id>/", views.topic, name="topic"),
    path("new_topic/", views.new_topic, name="new_topic"),
    path("new_entry/<int:topic_id>/", views.new_entry, name="new_entry"),
    path("edit_entry/<int:entry_id>/", views.edit_entry, name="edit_entry"),
]
