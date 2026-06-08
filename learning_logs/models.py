import markdown
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe


class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.text


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
        return self.comments.filter(parent__isnull=True)

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
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"

    @property
    def depth(self):
        d = 0
        parent = self.parent
        while parent is not None:
            d += 1
            parent = parent.parent
        return d
