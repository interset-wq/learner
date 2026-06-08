from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Question, Choice
from config.mixins import LoadMoreMixin


def index(request):
    return render(request, 'core/index.html')


class QuestionListView(LoadMoreMixin, ListView):
    model = Question
    template_name = 'core/question_list.html'
    context_object_name = 'latest_question_list'
    paginate_by = 10
    item_template = 'core/partials/question_items.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     context = {'question': question}
#     return render(request, 'core/detail.html', context)
class QuestionDetailView(DetailView):
    model = Question
    template_name = 'core/detail.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'core/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('core:results', args=(question.id,)))


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'core/results.html', {
#         'question': question,
#     })
class ResultsDetailView(DetailView):
    model = Question
    template_name = 'core/results.html'
