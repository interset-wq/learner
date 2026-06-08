from django.urls import path

from . import views

app_name = "learning_logs"

urlpatterns = [
    path("", views.index, name="index"),
    path("topics/", views.TopicListView.as_view(), name="topics"),
    path("explore/", views.PublicTopicListView.as_view(), name="public_topics"),
    path("topics/<int:topic_id>/", views.topic, name="topic"),
    path("entry/<int:entry_id>/", views.entry_detail, name="entry_detail"),
    path("new_topic/", views.new_topic, name="new_topic"),
    path("edit_topic/<int:topic_id>/", views.edit_topic, name="edit_topic"),
    path("delete_topic/<int:topic_id>/", views.delete_topic, name="delete_topic"),
    path(
        "delete_topic/<int:topic_id>/confirm/",
        views.delete_topic_confirm,
        name="delete_topic_confirm",
    ),
    path("new_entry/<int:topic_id>/", views.new_entry, name="new_entry"),
    path("edit_entry/<int:entry_id>/", views.edit_entry, name="edit_entry"),
    path(
        "delete_entry/<int:entry_id>/confirm/",
        views.delete_entry_confirm,
        name="delete_entry_confirm",
    ),
    path("delete_entry/<int:entry_id>/", views.delete_entry, name="delete_entry"),
    path("entry/<int:entry_id>/like/", views.toggle_like, name="toggle_like"),
    path("entry/<int:entry_id>/comment/", views.add_comment, name="add_comment"),
    path(
        "entry/<int:entry_id>/comments/",
        views.load_more_comments,
        name="load_more_comments",
    ),
    path(
        "comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path(
        "comment/<int:comment_id>/reply/",
        views.reply_comment,
        name="reply_comment",
    ),
]
