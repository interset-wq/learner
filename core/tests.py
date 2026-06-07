from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question, Choice

# Create your tests here.

##############
# Model test #
##############

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


#############
# View test #
#############

def create_question(question_text, days):
    time = timezone.now() + timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    return question

class QuestionIndexViewTest(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No questions found.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_questions(self):
        question = create_question('Past question text', days=-30)
        response = self.client.get(reverse('core:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question])

    def test_future_questions(self):
        create_question('Future question text', days=30)
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'No questions found.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_questions(self):
        question = create_question('Past question text', days=-30)
        create_question('Future question text', days=30)
        response = self.client.get(reverse('core:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question])

    def test_two_past_questions(self):
        question1 = create_question('Past question text1', days=-30)
        question2 = create_question('Past question text2', days=-5)
        response = self.client.get(reverse('core:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question2, question1])