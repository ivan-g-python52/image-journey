from django.conf import settings
from django.db import models
from django.urls import reverse


class Album(models.Model):
    """Альбом — коллекция постов одного пользователя."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='albums',
        verbose_name='Владелец',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name='Публичный',
        help_text='Публичные альбомы видны всем, приватные — только вам',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('albums:detail', kwargs={'pk': self.pk})

    @property
    def posts_count(self):
        return self.items.count()

    @property
    def cover_post(self):
        """Первый пост альбома — как обложка."""
        first_item = self.items.select_related('post').first()
        return first_item.post if first_item else None


class AlbumItem(models.Model):
    """Связь альбома и поста. Один пост может быть в разных альбомах."""
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Альбом',
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='album_items',
        verbose_name='Пост',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент альбома'
        verbose_name_plural = 'Элементы альбомов'
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['album', 'post'],
                name='unique_post_per_album',
            ),
        ]

    def __str__(self):
        return f'{self.post} в «{self.album}»'