from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Entry, Topic


def create_user(username="testuser", password="testpass123"):
    return User.objects.create_user(username, f"{username}@test.com", password)


def create_topic(user, text="Test Topic", is_public=False):
    return Topic.objects.create(text=text, owner=user, is_public=is_public)


def create_entry(topic, text="Test entry text.", title="Test Entry", is_public=False):
    return Entry.objects.create(
        text=text, topic=topic, title=title, is_public=is_public
    )


class TopicModelTest(TestCase):
    def test_str(self):
        user = create_user()
        topic = Topic(text="Django Basics", owner=user)
        self.assertEqual(str(topic), "Django Basics")

    def test_default_is_private(self):
        user = create_user()
        topic = Topic(text="Test", owner=user)
        self.assertFalse(topic.is_public)


class EntryModelTest(TestCase):
    def test_str(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(title="My Entry", text="content", topic=topic)
        self.assertEqual(str(entry), "My Entry")

    def test_default_is_private(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(title="Test", text="content", topic=topic)
        self.assertFalse(entry.is_public)

    def test_rendered_text_markdown(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(
            title="Test", text="# Heading\n\n**bold** and *italic*", topic=topic
        )
        html = entry.rendered_text
        self.assertIn("<h1", html)
        self.assertIn("Heading", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)

    def test_rendered_text_code_block(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(title="Test", text='```python\nprint("hello")\n```', topic=topic)
        html = entry.rendered_text
        self.assertIn("highlight", html)
        self.assertIn("print", html)


class IndexViewTest(TestCase):
    def test_index_status_code(self):
        response = self.client.get(reverse("learning_logs:index"))
        self.assertEqual(response.status_code, 200)


class TopicListViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("learning_logs:topics"))
        self.assertEqual(response.status_code, 302)

    def test_shows_user_topics(self):
        user = create_user()
        self.client.force_login(user)
        create_topic(user, "My Topic")
        other = create_user("other")
        create_topic(other, "Other Topic")
        response = self.client.get(reverse("learning_logs:topics"))
        self.assertContains(response, "My Topic")
        self.assertNotContains(response, "Other Topic")


class TopicDetailViewTest(TestCase):
    def test_private_topic_returns_404_for_anonymous(self):
        user = create_user()
        topic = create_topic(user)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_view(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, "Django Basics")
        entry = create_entry(topic, "My Entry", title="Entry Title")
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertContains(response, "Django Basics")
        self.assertContains(response, "Entry Title")

    def test_other_user_cannot_view_private(self):
        owner = create_user("owner")
        other = create_user("other")
        self.client.force_login(other)
        topic = create_topic(owner)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_can_view_public_topic(self):
        owner = create_user("owner")
        topic = create_topic(owner, "Public Topic", is_public=True)
        create_entry(topic, "content", title="Public Entry", is_public=True)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Topic")
        self.assertContains(response, "Public Entry")

    def test_other_user_can_view_public_topic(self):
        owner = create_user("owner")
        other = create_user("other")
        self.client.force_login(other)
        topic = create_topic(owner, "Public Topic", is_public=True)
        entry = create_entry(topic, "content", title="Public Entry", is_public=True)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertContains(response, "Public Topic")
        self.assertContains(response, "Public Entry")

    def test_public_topic_hides_private_entries(self):
        owner = create_user("owner")
        other = create_user("other")
        self.client.force_login(other)
        topic = create_topic(owner, "Public Topic", is_public=True)
        create_entry(topic, "content", title="Private Entry", is_public=False)
        create_entry(topic, "content", title="Public Entry", is_public=True)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertContains(response, "Public Entry")
        self.assertNotContains(response, "Private Entry")

    def test_owner_sees_all_entries(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, "My Topic")
        create_entry(topic, "content", title="Private Entry", is_public=False)
        create_entry(topic, "content", title="Public Entry", is_public=True)
        response = self.client.get(reverse("learning_logs:topic", args=[topic.id]))
        self.assertContains(response, "Private Entry")
        self.assertContains(response, "Public Entry")


class NewTopicViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("learning_logs:new_topic"))
        self.assertEqual(response.status_code, 302)

    def test_create_topic(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.post(
            reverse("learning_logs:new_topic"), {"text": "New Topic"}
        )
        self.assertRedirects(response, reverse("learning_logs:topics"))
        self.assertTrue(Topic.objects.filter(text="New Topic", owner=user).exists())

    def test_create_public_topic(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.post(
            reverse("learning_logs:new_topic"), {"text": "Public", "is_public": "on"}
        )
        self.assertRedirects(response, reverse("learning_logs:topics"))
        topic = Topic.objects.get(text="Public", owner=user)
        self.assertTrue(topic.is_public)


class NewEntryViewTest(TestCase):
    def test_create_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user)
        response = self.client.post(
            reverse("learning_logs:new_entry", args=[topic.id]),
            {"title": "New Entry", "text": "New entry content"},
        )
        self.assertRedirects(response, reverse("learning_logs:topic", args=[topic.id]))
        self.assertTrue(Entry.objects.filter(title="New Entry", topic=topic).exists())

    def test_create_public_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, "Public Topic", is_public=True)
        response = self.client.post(
            reverse("learning_logs:new_entry", args=[topic.id]),
            {"title": "Public", "text": "content", "is_public": "on"},
        )
        self.assertRedirects(response, reverse("learning_logs:topic", args=[topic.id]))
        entry = Entry.objects.get(title="Public", topic=topic)
        self.assertTrue(entry.is_public)

    def test_private_topic_entry_is_forced_private(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, "Private Topic", is_public=False)
        entry = Entry(title="Test", text="content", topic=topic, is_public=True)
        entry.save()
        self.assertFalse(entry.is_public)


class EditEntryViewTest(TestCase):
    def test_edit_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user)
        entry = create_entry(topic, "Original text", title="Original")
        response = self.client.post(
            reverse("learning_logs:edit_entry", args=[entry.id]),
            {"title": "Updated", "text": "Updated text"},
        )
        self.assertRedirects(response, reverse("learning_logs:topic", args=[topic.id]))
        entry.refresh_from_db()
        self.assertEqual(entry.title, "Updated")
        self.assertEqual(entry.text, "Updated text")


class PublicTopicListViewTest(TestCase):
    def test_no_login_required(self):
        response = self.client.get(reverse("learning_logs:public_topics"))
        self.assertEqual(response.status_code, 200)

    def test_shows_only_public_topics(self):
        user = create_user()
        create_topic(user, "Private Topic", is_public=False)
        create_topic(user, "Public Topic", is_public=True)
        response = self.client.get(reverse("learning_logs:public_topics"))
        self.assertContains(response, "Public Topic")
        self.assertNotContains(response, "Private Topic")

    def test_shows_topics_from_multiple_users(self):
        user1 = create_user("user1")
        user2 = create_user("user2")
        create_topic(user1, "User1 Public", is_public=True)
        create_topic(user2, "User2 Public", is_public=True)
        response = self.client.get(reverse("learning_logs:public_topics"))
        self.assertContains(response, "User1 Public")
        self.assertContains(response, "User2 Public")
