from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from config.mixins import LoadMoreMixin
from learning_logs.forms import CommentForm, EntryForm, TopicForm
from learning_logs.models import Comment, Entry, Topic

COMMENTS_PER_PAGE = 10


def _is_htmx(request):
    return request.headers.get("HX-Request") == "true"


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
    entry = get_object_or_404(
        Entry.objects.select_related("topic", "topic__owner"), pk=entry_id
    )
    topic = entry.topic
    is_owner = request.user.is_authenticated and topic.owner == request.user
    if not is_owner and (not topic.is_public or not entry.is_public):
        raise Http404

    root_comments = (
        entry.comments.filter(parent__isnull=True)
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=Comment.objects.select_related("user"),
            )
        )
    )

    total_comments = entry.comments.count()
    root_count = root_comments.count()
    shown_comments = root_comments[:COMMENTS_PER_PAGE]
    has_more = root_count > COMMENTS_PER_PAGE
    liked = (
        request.user.is_authenticated
        and entry.liked_by.filter(pk=request.user.pk).exists()
    )

    context = {
        "entry": entry,
        "topic": topic,
        "is_owner": is_owner,
        "topic_owner": topic.owner,
        "root_comments": shown_comments,
        "has_more_comments": has_more,
        "total_comments": total_comments,
        "shown_count": min(root_count, COMMENTS_PER_PAGE),
        "liked": liked,
    }
    return render(request, "learning_logs/entry_detail.html", context)


def load_more_comments(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if not entry.topic.is_public or not entry.is_public:
        raise Http404
    offset = int(request.GET.get("offset", 0))
    limit = COMMENTS_PER_PAGE

    root_comments = (
        entry.comments.filter(parent__isnull=True)
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=Comment.objects.select_related("user"),
            )
        )[offset : offset + limit]
    )

    total_root = entry.comments.filter(parent__isnull=True).count()
    has_more = (offset + limit) < total_root

    html = render_to_string(
        "learning_logs/components/comment_thread.html",
        {
            "comments": root_comments,
            "user": request.user,
            "topic_owner": entry.topic.owner,
        },
    )

    if has_more:
        load_more_html = f"""
        <div id="load-more-marker" hx-get="/learning_logs/entry/{entry.id}/comments/?offset={offset + limit}"
             hx-trigger="revealed" hx-swap="outerHTML" hx-target="this"></div>
        """
        html += load_more_html

    return HttpResponse(html)


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
def edit_topic(request, topic_id):
    t = get_object_or_404(Topic, pk=topic_id)
    if t.owner != request.user:
        raise Http404
    if request.method != "POST":
        form = TopicForm(instance=t)
    else:
        form = TopicForm(data=request.POST, instance=t)
        if form.is_valid():
            form.save()
            return redirect(reverse("learning_logs:topic", args=[t.id]))
    context = {"form": form, "topic": t}
    return render(request, "learning_logs/edit_topic.html", context)


@login_required
@require_POST
def delete_topic(request, topic_id):
    t = get_object_or_404(Topic, pk=topic_id)
    if t.owner != request.user:
        raise Http404
    t.delete()
    return redirect(reverse("learning_logs:topics"))


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

    html = render_to_string(
        "learning_logs/components/like_button.html",
        {"entry": entry, "liked": liked, "user": request.user},
    )
    return HttpResponse(html)


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
        html = render_to_string(
            "learning_logs/components/comment_item.html",
            {
                "comment": comment,
                "user": request.user,
                "topic_owner": entry.topic.owner,
            },
        )
        count_html = (
            f'<span id="comment-count" hx-swap-oob="true">{entry.comment_count}</span>'
        )
        return HttpResponse(html + count_html)
    return HttpResponse(status=400)


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    entry = comment.entry
    if comment.user != request.user and entry.topic.owner != request.user:
        raise Http404
    comment.delete()
    count_html = (
        f'<span id="comment-count" hx-swap-oob="true">{entry.comment_count}</span>'
    )
    return HttpResponse(count_html)


@login_required
@require_POST
def reply_comment(request, comment_id):
    parent = get_object_or_404(
        Comment.objects.select_related("entry", "entry__topic"), pk=comment_id
    )
    entry = parent.entry
    if not entry.topic.is_public or not entry.is_public:
        raise Http404
    if parent.parent_id is not None:
        raise Http404
    text = request.POST.get("text", "").strip()
    if text:
        mention = f"@{parent.user.username} "
        if not text.startswith("@"):
            text = mention + text
        comment = Comment.objects.create(
            entry=entry, user=request.user, parent=parent, text=text
        )
        html = render_to_string(
            "learning_logs/components/comment_item.html",
            {
                "comment": comment,
                "user": request.user,
                "topic_owner": entry.topic.owner,
            },
            request=request,
        )
        count_html = (
            f'<span id="comment-count" hx-swap-oob="true">{entry.comment_count}</span>'
        )
        return HttpResponse(html + count_html)
    return HttpResponse(status=400)
