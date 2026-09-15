from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Tag(models.Model):
    """Тег для постов. slug генерируется автоматически."""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        blank=True,
        verbose_name='Slug (для URL)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    """Пост — картинка + описание + теги."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/',
        verbose_name='Изображение',
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
        verbose_name='Теги',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f'Пост #{self.pk}'

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class Like(models.Model):
    """Лайк поста. Один пользователь — один лайк на пост."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_like_per_user_post',
            ),
        ]

    def __str__(self):
        return f'{self.user} ♥ {self.post}'


class Comment(models.Model):
    """Комментарий к посту."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(max_length=1000, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.text[:30]}'


class CommentLike(models.Model):
    """Лайк комментария."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes',
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лайк комментария'
        verbose_name_plural = 'Лайки комментариев'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_like_per_user_comment',
            ),
        ]

    def __str__(self):
        return f'{self.user} ♥ {self.comment}'