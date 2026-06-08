from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from config.mixins import LoadMoreMixin
from learning_logs.form import EntryForm, TopicForm
from learning_logs.models import Entry, Topic


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
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
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
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(data=request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect(reverse("learning_logs:topic", args=[topic.id]))
    context = {"form": form, "topic": topic, "entry": entry}
    return render(request, "learning_logs/edit_entry.html", context)
