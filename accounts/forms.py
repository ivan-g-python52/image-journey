from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


INPUT_CLASS = (
    'w-full bg-surface-700 border border-surface-600 rounded-lg '
    'px-4 py-2.5 text-ink-100 placeholder-ink-500 '
    'focus:outline-none focus:border-accent-500 transition'
)


class RegisterForm(UserCreationForm):
    """Форма регистрации."""

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'you@example.com',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'username',
            }),
        }
        labels = {
            'username': 'Имя пользователя',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стили для встроенных полей пароля
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASS,
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASS,
            'placeholder': 'Повторите пароль',
        })
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'

    def clean_email(self):
        """Проверяем уникальность email."""
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class ProfileEditForm(forms.ModelForm):
    """Редактирование профиля."""

    class Meta:
        model = User
        fields = ('avatar', 'bio')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'w-full text-ink-300 file:mr-4 file:py-2 file:px-4 '
                         'file:rounded-lg file:border-0 file:bg-accent-600 '
                         'file:text-white hover:file:bg-accent-500 '
                         'file:cursor-pointer cursor-pointer',
                'accept': 'image/*',
            }),
            'bio': forms.Textarea(attrs={
                'class': INPUT_CLASS + ' resize-none',
                'rows': 4,
                'placeholder': 'Расскажи о себе...',
            }),
        }