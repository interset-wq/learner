from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from config.mixins import LoadMoreMixin
from learning_logs.forms import CommentForm, EntryForm, TopicForm
from learning_logs.models import Comment, Entry, Topic


def index(request):
    return render(request, "learning_logs/index.html")


class TopicListView(LoadMoreMixin, LoginRequiredMixin, ListView):
    model = Topic
    template_name = "learning_logs/topics.html"
    context_object_name = "topics"
    paginate_by = 10
    item_template = "learning_logs/partials/topic_items.html"

    def get_queryset(self):
        return Topic.objects.filter(owner=self.request.user).order_by("-date_added")


class PublicTopicListView(LoadMoreMixin, ListView):
    model = Topic
    template_name = "learning_logs/public_topics.html"
    context_object_name = "topics"
    paginate_by = 10
    item_template = "learning_logs/partials/topic_items.html"

    def get_queryset(self):
        return Topic.objects.filter(is_public=True).order_by("-date_added")


def topic(request, topic_id):
    t = get_object_or_404(Topic, pk=topic_id)
    is_owner = request.user.is_authenticated and t.owner == request.user
    if not is_owner and not t.is_public:
        raise Http404
    entries = t.entry_set.all()
    if not is_owner:
        entries = entries.filter(is_public=True)
    context = {"topic": t, "entries": entries, "is_owner": is_owner}
    return render(request, "learning_logs/topic.html", context)


def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    is_owner = request.user.is_authenticated and topic.owner == request.user
    if not is_owner and (not topic.is_public or not entry.is_public):
        raise Http404
    context = {
        "entry": entry,
        "topic": topic,
        "is_owner": is_owner,
        "topic_owner": topic.owner,
    }
    return render(request, "learning_logs/entry_detail.html", context)


@login_required
def new_topic(request):
    if request.method != "POST":
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.owner = request.user
            topic.save()
            return redirect(reverse("learning_logs:topics"))
    context = {"form": form}
    return render(request, "learning_logs/new_topic.html", context)


@login_required
def new_entry(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if topic.owner != request.user:
        raise Http404
    if request.method != "POST":
        form = EntryForm(topic=topic)
    else:
        form = EntryForm(data=request.POST, topic=topic)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.topic = topic
            entry.save()
            return redirect(reverse("learning_logs:topic", args=[topic.id]))
    context = {"form": form, "topic": topic}
    return render(request, "learning_logs/new_entry.html", context)


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404
    if request.method != "POST":
        form = EntryForm(instance=entry, topic=topic)
    else:
        form = EntryForm(data=request.POST, instance=entry, topic=topic)
        if form.is_valid():
            form.save()
            return redirect(reverse("learning_logs:topic", args=[topic.id]))
    context = {"form": form, "topic": topic, "entry": entry}
    return render(request, "learning_logs/edit_entry.html", context)


@login_required
@require_POST
def toggle_like(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if not entry.topic.is_public or not entry.is_public:
        raise Http404
    if request.user in entry.liked_by.all():
        entry.liked_by.remove(request.user)
        liked = False
    else:
        entry.liked_by.add(request.user)
        liked = True
    return JsonResponse({"liked": liked, "count": entry.like_count})


def _render_comment_html(comment, user, topic_owner):
    return render_to_string(
        "learning_logs/components/comment_item.html",
        {"comment": comment, "user": user, "topic_owner": topic_owner},
    )


@login_required
@require_POST
def add_comment(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if not entry.topic.is_public or not entry.is_public:
        raise Http404
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.entry = entry
        comment.user = request.user
        comment.save()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = _render_comment_html(comment, request.user, entry.topic.owner)
            return JsonResponse(
                {"success": True, "html": html, "count": entry.comment_count}
            )
    return redirect(reverse("learning_logs:entry_detail", args=[entry.id]))


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    entry = comment.entry
    if comment.user != request.user and entry.topic.owner != request.user:
        raise Http404
    comment_id = comment.id
    comment.delete()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": True, "comment_id": comment_id, "count": entry.comment_count}
        )
    return redirect(reverse("learning_logs:entry_detail", args=[entry.id]))


@login_required
@require_POST
def reply_comment(request, comment_id):
    parent = get_object_or_404(Comment, pk=comment_id)
    entry = parent.entry
    if not entry.topic.is_public or not entry.is_public:
        raise Http404
    text = request.POST.get("text", "").strip()
    if text:
        comment = Comment.objects.create(
            entry=entry, user=request.user, parent=parent, text=text
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = _render_comment_html(comment, request.user, entry.topic.owner)
            return JsonResponse(
                {
                    "success": True,
                    "html": html,
                    "parent_id": parent.id,
                    "count": entry.comment_count,
                }
            )
    return redirect(reverse("learning_logs:entry_detail", args=[entry.id]))
