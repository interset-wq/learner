from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def create_question(question_text, days=0, choices=None):
    pub_date = timezone.now() + timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=pub_date)
    if choices:
        for choice_text, votes in choices:
            Choice.objects.create(
                question=question, choice_text=choice_text, votes=votes
            )
    return question


class QuestionModelTest(TestCase):
    def test_str(self):
        question = Question(question_text="What is Django?")
        self.assertEqual(str(question), "What is Django?")

    def test_was_published_recently_with_future(self):
        future = create_question("Future question", days=30)
        self.assertFalse(future.was_published_recently())

    def test_was_published_recently_with_old(self):
        old = create_question("Old question", days=-2)
        self.assertFalse(old.was_published_recently())

    def test_was_published_recently_with_recent(self):
        recent = create_question("Recent question", days=-0.5)
        self.assertTrue(recent.was_published_recently())


class ChoiceModelTest(TestCase):
    def test_str(self):
        q = create_question("Test?")
        c = Choice(question=q, choice_text="Yes")
        self.assertEqual(str(c), "Yes")


class IndexViewTest(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)

    def test_past_question(self):
        create_question("Past question", days=-30)
        response = self.client.get(reverse("core:questions"))
        self.assertContains(response, "Past question")

    def test_future_question(self):
        create_question("Future question", days=30)
        response = self.client.get(reverse("core:questions"))
        self.assertNotContains(response, "Future question")


class QuestionListViewTest(TestCase):
    def test_list_view(self):
        create_question("Q1", days=-1)
        create_question("Q2", days=-2)
        response = self.client.get(reverse("core:questions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Q1")
        self.assertContains(response, "Q2")


class DetailViewTest(TestCase):
    def test_past_question(self):
        past = create_question("Past", days=-5, choices=[("Yes", 0), ("No", 0)])
        response = self.client.get(reverse("core:detail", args=[past.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past")

    def test_nonexistent_question(self):
        response = self.client.get(reverse("core:detail", args=[999]))
        self.assertEqual(response.status_code, 404)


class VoteViewTest(TestCase):
    def setUp(self):
        self.question = create_question(
            "Vote test", days=-1, choices=[("Choice A", 0), ("Choice B", 0)]
        )
        self.choice_a = self.question.choice_set.first()

    def test_vote_increments(self):
        response = self.client.post(
            reverse("core:vote", args=[self.question.id]), {"choice": self.choice_a.id}
        )
        self.assertRedirects(response, reverse("core:results", args=[self.question.id]))
        self.choice_a.refresh_from_db()
        self.assertEqual(self.choice_a.votes, 1)

    def test_vote_no_choice(self):
        response = self.client.post(reverse("core:vote", args=[self.question.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "select a choice")


class ResultsViewTest(TestCase):
    def test_results(self):
        q = create_question("Results test", days=-1, choices=[("A", 5), ("B", 3)])
        response = self.client.get(reverse("core:results", args=[q.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A")
        self.assertContains(response, "B")
