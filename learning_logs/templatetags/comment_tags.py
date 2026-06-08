from django import template

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
