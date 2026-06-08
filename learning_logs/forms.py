from django import forms

from .models import Comment, Entry, Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["text", "is_public"]
        labels = {"text": "", "is_public": "Make this topic public"}
        widgets = {"is_public": forms.CheckboxInput(attrs={"class": "mr-2"})}


class EntryForm(forms.ModelForm):
    def __init__(self, *args, topic=None, **kwargs):
        super().__init__(*args, **kwargs)
        if topic and not topic.is_public:
            del self.fields["is_public"]

    class Meta:
        model = Entry
        fields = ["title", "text", "is_public"]
        labels = {"title": "", "text": "", "is_public": "Make this entry public"}
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Entry title"}),
            "is_public": forms.CheckboxInput(attrs={"class": "mr-2"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Write a comment...",
                    "class": "input-field",
                }
            ),
        }
        labels = {"text": ""}
