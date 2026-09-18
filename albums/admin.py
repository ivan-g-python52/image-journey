from django.contrib import admin
from .models import Album, AlbumItem


class AlbumItemInline(admin.TabularInline):
    model = AlbumItem
    extra = 1
    autocomplete_fields = ['post']
    verbose_name = 'Пост в альбоме'
    verbose_name_plural = 'Посты в альбоме'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'posts_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AlbumItemInline]

    def posts_count(self, obj):
        return obj.items.count()
    posts_count.short_description = 'Постов'


@admin.register(AlbumItem)
class AlbumItemAdmin(admin.ModelAdmin):
    list_display = ('album', 'post', 'added_at')
    list_filter = ('added_at',)
    autocomplete_fields = ['album', 'post']