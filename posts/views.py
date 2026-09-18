from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import PostForm, CommentForm
from .models import Post, Comment, Like, CommentLike, Tag
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def feed(request):
    """Главная лента — посты с пагинацией."""
    posts_list = Post.objects.select_related('author').prefetch_related('tags', 'likes')

    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/feed.html', {'page_obj': page_obj})

def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related(
            'tags', 'comments__author', 'comments__likes',
        ),
        pk=pk,
    )
    comments = post.comments.select_related('author').prefetch_related('likes')
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()          # сохранит пост И теги
            messages.success(request, 'Пост опубликован!')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})

@login_required
@require_POST
def toggle_post_like(request, pk):
    """AJAX: поставить/снять лайк с поста."""
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'count': post.likes.count(),
    })


@login_required
@require_POST
def toggle_comment_like(request, pk):
    """AJAX: поставить/снять лайк с комментария."""
    comment = get_object_or_404(Comment, pk=pk)
    like, created = CommentLike.objects.get_or_create(
        user=request.user, comment=comment,
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'count': comment.likes.count(),
    })

@login_required
@require_POST
def comment_create(request, pk):
    """Добавить комментарий к посту."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, 'Комментарий добавлен')
    else:
        messages.error(request, 'Комментарий не может быть пустым')

    return redirect('posts:detail', pk=post.pk)

def search(request):
    """Поиск постов по заголовку, описанию и тегам."""
    query = request.GET.get('q', '').strip()
    posts_list = Post.objects.none()

    if query:
        posts_list = Post.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).select_related('author').prefetch_related('tags', 'likes').distinct()

    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/search.html', {
        'query': query,
        'page_obj': page_obj,
        'total_count': paginator.count,   # для «найдено N постов»
    })

@login_required
def post_edit(request, pk):
    """Редактирование поста. Только автор."""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        raise PermissionDenied('Вы не можете редактировать чужой пост')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Подставляем теги из tags_input
            post = form.save(commit=False)
            post.author = request.user  # на всякий случай
            form.save()
            messages.success(request, 'Пост обновлён')
            return redirect('posts:detail', pk=post.pk)
    else:
        # Заполняем поле тегов текущими тегами поста
        initial_tags = ', '.join(post.tags.values_list('name', flat=True))
        form = PostForm(instance=post, initial={'tags_input': initial_tags})

    return render(request, 'posts/post_edit.html', {
        'form': form,
        'post': post,
    })


@login_required
@require_POST
def post_delete(request, pk):
    """Удаление поста. Только автор."""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        raise PermissionDenied('Вы не можете удалить чужой пост')

    post.delete()
    messages.success(request, 'Пост удалён')
    return redirect('posts:feed')


@login_required
@require_POST
def comment_delete(request, pk):
    """Удаление комментария. Автор комментария или автор поста."""
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    # Удалять может автор комментария или автор поста
    if comment.author != request.user and post.author != request.user:
        raise PermissionDenied('У вас нет прав на удаление этого комментария')

    comment.delete()
    messages.success(request, 'Комментарий удалён')
    return redirect('posts:detail', pk=post.pk)