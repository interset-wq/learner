from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Comment, Entry, Topic


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


class LikeTest(TestCase):
    def test_toggle_like(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        url = reverse("learning_logs:toggle_like", args=[entry.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"like-btn", response.content)
        self.assertTrue(entry.liked_by.filter(pk=user.pk).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(entry.liked_by.filter(pk=user.pk).exists())

    def test_like_requires_login(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        url = reverse("learning_logs:toggle_like", args=[entry.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_cannot_like_private_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=False)
        url = reverse("learning_logs:toggle_like", args=[entry.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_like_private_topic_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=False)
        entry = create_entry(topic, "content", title="Test", is_public=False)
        url = reverse("learning_logs:toggle_like", args=[entry.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class CommentTest(TestCase):
    def test_add_comment(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        url = reverse("learning_logs:add_comment", args=[entry.id])
        response = self.client.post(url, {"text": "Great post!"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(entry=entry, user=user, text="Great post!").exists()
        )

    def test_add_comment_requires_login(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        url = reverse("learning_logs:add_comment", args=[entry.id])
        response = self.client.post(url, {"text": "Hi"})
        self.assertEqual(response.status_code, 302)

    def test_cannot_comment_on_private_entry(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=False)
        url = reverse("learning_logs:add_comment", args=[entry.id])
        response = self.client.post(url, {"text": "Hi"})
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_by_author(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="My comment")
        url = reverse("learning_logs:delete_comment", args=[comment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=comment.id).exists())

    def test_delete_comment_by_topic_owner(self):
        owner = create_user("owner")
        commenter = create_user("commenter")
        self.client.force_login(owner)
        topic = create_topic(owner, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=commenter, text="Hello")
        url = reverse("learning_logs:delete_comment", args=[comment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=comment.id).exists())

    def test_cannot_delete_others_comment(self):
        owner = create_user("owner")
        commenter = create_user("commenter")
        other = create_user("other")
        self.client.force_login(other)
        topic = create_topic(owner, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=commenter, text="Hello")
        url = reverse("learning_logs:delete_comment", args=[comment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class EntryModelLikeCommentTest(TestCase):
    def test_like_count(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        self.assertEqual(entry.like_count, 0)
        entry.liked_by.add(user)
        self.assertEqual(entry.like_count, 1)

    def test_comment_count(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        self.assertEqual(entry.comment_count, 0)
        Comment.objects.create(entry=entry, user=user, text="Hi")
        self.assertEqual(entry.comment_count, 1)

    def test_likes_preserved_when_topic_becomes_private(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        entry.liked_by.add(user)
        Comment.objects.create(entry=entry, user=user, text="Hi")
        topic.is_public = False
        topic.save()
        entry.refresh_from_db()
        self.assertEqual(entry.like_count, 1)
        self.assertEqual(entry.comment_count, 1)

    def test_root_comments(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        root = Comment.objects.create(entry=entry, user=user, text="Root")
        Comment.objects.create(entry=entry, user=user, text="Reply", parent=root)
        self.assertEqual(entry.root_comments.count(), 1)
        self.assertEqual(entry.root_comments.first(), root)

    def test_comment_depth(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        c1 = Comment.objects.create(entry=entry, user=user, text="L1")
        c2 = Comment.objects.create(entry=entry, user=user, text="L2", parent=c1)
        self.assertFalse(c1.is_reply)
        self.assertTrue(c2.is_reply)
        with self.assertRaises(ValueError):
            Comment.objects.create(entry=entry, user=user, text="L3", parent=c2)


class ReplyCommentTest(TestCase):
    def test_reply_to_comment(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="Original")
        url = reverse("learning_logs:reply_comment", args=[comment.id])
        response = self.client.post(url, {"text": "My reply"})
        self.assertEqual(response.status_code, 200)
        reply = Comment.objects.get(parent=comment)
        self.assertIn("@testuser", reply.text)
        self.assertIn("My reply", reply.text)
        self.assertEqual(reply.user, user)

    def test_reply_requires_login(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="Original")
        url = reverse("learning_logs:reply_comment", args=[comment.id])
        response = self.client.post(url, {"text": "Reply"})
        self.assertEqual(response.status_code, 302)

    def test_reply_preserves_existing_mention(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="Original")
        url = reverse("learning_logs:reply_comment", args=[comment.id])
        response = self.client.post(url, {"text": "@testuser already mentioned"})
        self.assertEqual(response.status_code, 200)
        reply = Comment.objects.get(parent=comment)
        self.assertEqual(reply.text, "@testuser already mentioned")

    def test_reply_preserves_existing_at_sign(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="Original")
        url = reverse("learning_logs:reply_comment", args=[comment.id])
        response = self.client.post(url, {"text": "@someone else's comment"})
        self.assertEqual(response.status_code, 200)
        reply = Comment.objects.get(parent=comment)
        self.assertTrue(reply.text.startswith("@someone"))

    def test_reply_requires_login(self):
        user = create_user()
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        comment = Comment.objects.create(entry=entry, user=user, text="Original")
        url = reverse("learning_logs:reply_comment", args=[comment.id])
        response = self.client.post(url, {"text": "Reply"})
        self.assertEqual(response.status_code, 302)

    def test_cannot_reply_to_reply(self):
        user = create_user()
        self.client.force_login(user)
        topic = create_topic(user, is_public=True)
        entry = create_entry(topic, "content", title="Test", is_public=True)
        c1 = Comment.objects.create(entry=entry, user=user, text="L1")
        c2 = Comment.objects.create(entry=entry, user=user, text="L2", parent=c1)
        url = reverse("learning_logs:reply_comment", args=[c2.id])
        response = self.client.post(url, {"text": "L3 reply"})
        self.assertEqual(response.status_code, 404)
