from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import AlbumForm
from .models import Album, AlbumItem
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from posts.models import Post

@login_required
def album_list(request):
    """Список альбомов текущего пользователя."""
    albums = (
        Album.objects
        .filter(owner=request.user)
        .prefetch_related('items__post')
    )
    return render(request, 'albums/album_list.html', {'albums': albums})


@login_required
def album_create(request):
    """Создание альбома."""
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            messages.success(request, f'Альбом «{album.title}» создан')
            return redirect('albums:detail', pk=album.pk)
    else:
        form = AlbumForm()
    return render(request, 'albums/album_form.html', {
        'form': form,
        'action': 'create',
    })


def album_detail(request, pk):
    """Страница альбома. Приватные видны только владельцу."""
    album = get_object_or_404(
        Album.objects.select_related('owner').prefetch_related(
            'items__post__author',
            'items__post__tags',
            'items__post__likes',
        ),
        pk=pk,
    )

    # Приватный альбом — только для владельца
    if not album.is_public and request.user != album.owner:
        raise PermissionDenied('Это приватный альбом')

    is_owner = request.user == album.owner
    items = album.items.all()

    return render(request, 'albums/album_detail.html', {
        'album': album,
        'items': items,
        'is_owner': is_owner,
    })


@login_required
def album_edit(request, pk):
    """Редактирование альбома. Только владелец."""
    album = get_object_or_404(Album, pk=pk)

    if album.owner != request.user:
        raise PermissionDenied('Вы не можете редактировать чужой альбом')

    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, 'Альбом обновлён')
            return redirect('albums:detail', pk=album.pk)
    else:
        form = AlbumForm(instance=album)

    return render(request, 'albums/album_form.html', {
        'form': form,
        'album': album,
        'action': 'edit',
    })


@login_required
@require_POST
def album_delete(request, pk):
    """Удаление альбома. Только владелец."""
    album = get_object_or_404(Album, pk=pk)

    if album.owner != request.user:
        raise PermissionDenied('Вы не можете удалить чужой альбом')

    album.delete()
    messages.success(request, 'Альбом удалён')
    return redirect('albums:list')

@login_required
def api_album_list(request):
    """JSON: список своих альбомов + флаг, есть ли в них указанный пост."""
    post_id = request.GET.get('post')
    post = get_object_or_404(Post, pk=post_id) if post_id else None

    albums = Album.objects.filter(owner=request.user).prefetch_related('items')

    data = []
    for album in albums:
        has_post = post and album.items.filter(post=post).exists()
        data.append({
            'id': album.pk,
            'title': album.title,
            'is_public': album.is_public,
            'has_post': has_post,
            'posts_count': album.posts_count,
        })

    return JsonResponse({'albums': data})


@login_required
@require_POST
def api_toggle_post(request):
    """JSON: добавить/убрать пост из альбома."""
    try:
        payload = json.loads(request.body)
        album_id = payload.get('album_id')
        post_id = payload.get('post_id')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    album = get_object_or_404(Album, pk=album_id)
    post = get_object_or_404(Post, pk=post_id)

    if album.owner != request.user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    item, created = AlbumItem.objects.get_or_create(album=album, post=post)

    if not created:
        item.delete()
        has_post = False
    else:
        has_post = True

    return JsonResponse({
        'has_post': has_post,
        'posts_count': album.posts_count,
    })


@login_required
@require_POST
def api_create_album(request):
    """JSON: создать новый альбом и (опционально) добавить в него пост."""
    try:
        payload = json.loads(request.body)
        title = payload.get('title', '').strip()
        post_id = payload.get('post_id')
        is_public = payload.get('is_public', True)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title:
        return JsonResponse({'error': 'Введите название'}, status=400)

    album = Album.objects.create(
        owner=request.user,
        title=title[:200],
        is_public=is_public,
    )

    has_post = False
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        AlbumItem.objects.create(album=album, post=post)
        has_post = True

    return JsonResponse({
        'id': album.pk,
        'title': album.title,
        'is_public': album.is_public,
        'has_post': has_post,
        'posts_count': album.posts_count,
    })