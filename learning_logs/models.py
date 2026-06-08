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
