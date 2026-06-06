from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from learning_logs.form import TopicForm, EntryForm
from learning_logs.models import Topic, Entry


# Create your views here.
def index(request):
    return render(request, 'learning_logs/index.html')


def topics(request):
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    t = get_object_or_404(Topic, pk=topic_id)
    context = {'topic': t}
    return render(request, 'learning_logs/topic.html', context)


def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('learning_logs:topics'))
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


def new_entry(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.topic = topic
            entry.save()
            return redirect(reverse('learning_logs:topic', args=[topic.id]))
    context = {'form': form, 'topic': topic}
    return render(request, 'learning_logs/new_entry.html', context)


def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(data=request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect(reverse('learning_logs:topic', args=[topic.id]))
    context = {'form': form, 'topic': topic, 'entry': entry}
    return render(request, 'learning_logs/edit_entry.html', context)
