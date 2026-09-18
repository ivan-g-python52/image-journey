from django import forms
from .models import Album


INPUT_CLASS = (
    'w-full bg-surface-700 border border-surface-600 rounded-lg '
    'px-4 py-2.5 text-ink-100 placeholder-ink-500 '
    'focus:outline-none focus:border-accent-500 transition'
)


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Название альбома',
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASS + ' resize-none',
                'rows': 3,
                'placeholder': 'Зачем этот альбом? (необязательно)',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded accent-accent-600 cursor-pointer',
            }),
        }