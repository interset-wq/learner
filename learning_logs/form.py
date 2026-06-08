from django import forms

from .models import Topic, Entry


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text', 'is_public']
        labels = {'text': '', 'is_public': 'Make this topic public'}
        widgets = {'is_public': forms.CheckboxInput(attrs={'class': 'mr-2'})}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'text', 'is_public']
        labels = {'title': '', 'text': '', 'is_public': 'Make this entry public'}
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Entry title'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'mr-2'}),
        }
