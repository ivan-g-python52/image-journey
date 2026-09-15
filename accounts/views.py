from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from posts.models import Post
from .forms import RegisterForm, ProfileEditForm
from .models import User


def register(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('posts:feed')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу логиним
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('posts:feed')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request, username):
    """Страница профиля. Если это свой профиль — можно редактировать."""
    user_obj = get_object_or_404(User, username=username)
    posts = user_obj.posts.select_related('author').prefetch_related('tags', 'likes')

    is_own_profile = request.user == user_obj
    form = None

    if is_own_profile and request.method == 'POST':
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=user_obj,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('accounts:profile', username=user_obj.username)
    elif is_own_profile:
        form = ProfileEditForm(instance=user_obj)

    return render(request, 'accounts/profile.html', {
        'profile_user': user_obj,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'form': form,
    })