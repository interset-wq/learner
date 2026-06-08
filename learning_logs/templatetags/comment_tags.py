import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag(
    "learning_logs/components/comment_thread.html", takes_context=True
)
def render_comments(context, comments, topic_owner, depth=0):
    user = context.get("user")
    return {
        "comments": comments,
        "topic_owner": topic_owner,
        "user": user,
        "depth": depth,
    }


@register.filter(name="highlight_mentions")
def highlight_mentions(value):
    """Highlight @username mentions in comment text."""
    pattern = r"@(\w+)"
    replacement = r'<span class="text-blue-500 font-medium">@\1</span>'
    result = re.sub(pattern, replacement, str(value))
    return mark_safe(result)
