from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Topic, Entry


def create_user(username='testuser', password='testpass123'):
    return User.objects.create_user(username, f'{username}@test.com', password)


def create_topic(user, text='Test Topic'):
    return Topic.objects.create(text=text, owner=user)


def create_entry(topic, text='Test entry text.'):
    return Entry.objects.create(text=text, topic=topic)


class TopicModelTest(TestCase):
    def test_str(self):
        user = create_user()
        topic = Topic(text='Django Basics', owner=user)
        self.assertEqual(str(topic), 'Django Basics')


class EntryModelTest(TestCase):
    def test_str_short(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(text='Short text', topic=topic)
        self.assertEqual(str(entry), 'Short text')

    def test_str_long(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(text='A' * 100, topic=topic)
        result = str(entry)
        self.assertTrue(result.endswith('...'))
        self.assertLessEqual(len(result), 55)

    def test_rendered_text_markdown(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(text='# Heading\n\n**bold** and *italic*', topic=topic)
        html = entry.rendered_text
        self.assertIn('<h1', html)
        self.assertIn('Heading', html)
        self.assertIn('<strong>bold</strong>', html)
        self.assertIn('<em>italic</em>', html)

    def test_rendered_text_code_block(self):
        user = create_user()
        topic = create_topic(user)
        entry = Entry(text='```python\nprint("hello")\n```', topic=topic)
        html = entry.rendered_text
        self.assertIn('highlight', html)
        self.assertIn('print', html)


class IndexViewTest(TestCase):
    def test_index_status_code(self):
        response = self.client.get(reverse('learning_logs:index'))
        self.assertEqual(response.status_code, 200)


class TopicListViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('learning_logs:topics'))
        self.assertEqual(response.status_code, 302)

    def test_shows_user_topics(self):
        user = create_user()
        self.client.force_login(user)
        create_topic(user, 'My Topic')
        other = create_user('other')
        create_topic(other, 'Other Topic')
        response = self.client.get(reverse('learning_logs:topics'))
        self.assertContains(response, 'My Topic')
        self.assertNotContains(response, 'Other Topic')


class TopicDetailViewTest(TestCase):
    def test_requires_login(self):
        user = create_user()
        topic = create_topic(user)
        response = self.client.get(reverse('learning_logs:topic', args=[topic.id]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, 'Django Basics')
        entry = create_entry(topic, 'My Entry')
        response = self.client.get(reverse('learning_logs:topic', args=[topic.id]))
        self.assertContains(response, 'Django Basics')
        self.assertContains(response, 'My Entry')

    def test_other_user_cannot_view(self):
        owner = create_user('owner')
        other = create_user('other')
        self.client.force_login(other)
        topic = create_topic(owner)
        response = self.client.get(reverse('learning_logs:topic', args=[topic.id]))
        self.assertEqual(response.status_code, 404)


class NewTopicViewTest(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('learning_logs:new_topic'))
        self.assertEqual(response.status_code, 302)

    def test_create_topic(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.post(reverse('learning_logs:new_topic'), {'text': 'New Topic'})
        self.assertRedirects(response, reverse('learning_logs:topics'))
        self.assertTrue(Topic.objects.filter(text='New Topic', owner=user).exists())


class NewEntryViewTest(TestCase):
    def test_create_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user)
        response = self.client.post(
            reverse('learning_logs:new_entry', args=[topic.id]),
            {'text': 'New entry content'}
        )
        self.assertRedirects(response, reverse('learning_logs:topic', args=[topic.id]))
        self.assertTrue(Entry.objects.filter(text='New entry content', topic=topic).exists())


class EditEntryViewTest(TestCase):
    def test_edit_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user)
        entry = create_entry(topic, 'Original text')
        response = self.client.post(
            reverse('learning_logs:edit_entry', args=[entry.id]),
            {'text': 'Updated text'}
        )
        self.assertRedirects(response, reverse('learning_logs:topic', args=[topic.id]))
        entry.refresh_from_db()
        self.assertEqual(entry.text, 'Updated text')
