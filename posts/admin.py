from django.contrib import admin
from .models import Tag, Post, Like, Comment, CommentLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('created_at', 'author', 'tags')
    search_fields = ('title', 'description', 'author__username')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Лайков'

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Комментариев'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')