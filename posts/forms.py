from django import forms
from .models import Post, Tag, Comment


class PostForm(forms.ModelForm):
    """Форма загрузки поста с полем для тегов в стиле #тег1 #тег2."""

    tags_input = forms.CharField(
        required=False,
        label='Теги',
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-700 border border-surface-600 rounded-lg '
                     'px-4 py-2 text-ink-100 placeholder-ink-500 '
                     'focus:outline-none focus:border-accent-500 transition',
            'placeholder': 'например: природа, кот, закат',
        }),
        help_text='Введите теги через запятую или пробел',
    )

    class Meta:
        model = Post
        fields = ['image', 'title', 'description']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-ink-300 file:mr-4 file:py-2 file:px-4 '
                         'file:rounded-lg file:border-0 file:bg-accent-600 '
                         'file:text-white hover:file:bg-accent-500 '
                         'file:cursor-pointer cursor-pointer',
                'accept': 'image/*',
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-surface-700 border border-surface-600 rounded-lg '
                         'px-4 py-2 text-ink-100 placeholder-ink-500 '
                         'focus:outline-none focus:border-accent-500 transition',
                'placeholder': 'Дай название своему посту (необязательно)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-surface-700 border border-surface-600 rounded-lg '
                         'px-4 py-2 text-ink-100 placeholder-ink-500 '
                         'focus:outline-none focus:border-accent-500 transition '
                         'resize-none',
                'rows': 4,
                'placeholder': 'Расскажи о своей картинке...',
            }),
        }

    def clean_tags_input(self):
        """Разбиваем строку тегов на список уникальных названий."""
        raw = self.cleaned_data.get('tags_input', '')
        # Разделяем по запятой ИЛИ пробелу
        names = [n.strip() for n in raw.replace(',', ' ').split() if n.strip()]
        # Убираем дубли, сохраняя порядок
        seen = set()
        result = []
        for name in names:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                result.append(name[:50])  # обрезаем по max_length тега
        return result

    def save(self, commit=True):
        """Сохраняем пост и создаём/привязываем теги."""
        post = super().save(commit=False)
        if commit:
            post.save()
            tag_names = self.cleaned_data.get('tags_input', [])
            tags = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    name__iexact=name,
                    defaults={'name': name},
                )
                tags.append(tag)
            post.tags.set(tags)
        return post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full bg-surface-700 border border-surface-600 rounded-lg '
                         'px-4 py-2 text-ink-100 placeholder-ink-500 '
                         'focus:outline-none focus:border-accent-500 transition resize-none',
                'rows': 2,
                'placeholder': 'Напиши комментарий...',
            }),
        }