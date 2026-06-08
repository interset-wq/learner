import hashlib

import markdown
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import Truncator


class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.text


AVATAR_COLORS = [
    "from-blue-500 to-indigo-600",
    "from-emerald-500 to-teal-600",
    "from-purple-500 to-pink-600",
    "from-orange-500 to-red-600",
    "from-cyan-500 to-blue-600",
    "from-rose-500 to-fuchsia-600",
    "from-amber-500 to-orange-600",
    "from-lime-500 to-green-600",
]


class Entry(models.Model):
    title = models.CharField(max_length=200, default="Untitled")
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, related_name="liked_entries", blank=True)

    class Meta:
        verbose_name_plural = "entries"
        ordering = ["-date_added"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.topic.is_public:
            self.is_public = False
        super().save(*args, **kwargs)

    @property
    def like_count(self):
        return self.liked_by.count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def root_comments(self):
        return self.comments.filter(parent__isnull=True).select_related("user")

    @property
    def plain_text(self):
        return Truncator(self.text).chars(280)

    @property
    def rendered_preview(self):
        truncated = self.plain_text
        return mark_safe(
            markdown.markdown(
                truncated,
                extensions=["fenced_code", "codehilite", "tables"],
                extension_configs={
                    "codehilite": {"css_class": "highlight", "guess_lang": False}
                },
            )
        )

    @property
    def rendered_text(self):
        return mark_safe(
            markdown.markdown(
                self.text,
                extensions=["fenced_code", "codehilite", "tables", "toc"],
                extension_configs={
                    "codehilite": {"css_class": "highlight", "guess_lang": False}
                },
            )
        )


class Comment(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        limit_choices_to={"parent__isnull": True},
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"

    def save(self, *args, **kwargs):
        if self.parent and self.parent.parent_id is not None:
            raise ValueError("Cannot reply to a reply. Max depth is 2.")
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        return self.parent_id is not None

    @property
    def avatar_gradient(self):
        idx = int(hashlib.md5(self.user.username.encode()).hexdigest(), 16) % len(
            AVATAR_COLORS
        )
        return AVATAR_COLORS[idx]
