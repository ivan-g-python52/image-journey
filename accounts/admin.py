from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Доп. поля показываем в форме редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Профиль', {'fields': ('avatar', 'bio')}),
    )
    # Доп. поля в форме создания (для админа)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Профиль', {'fields': ('avatar', 'bio')}),
    )
    list_display = ('username', 'email', 'is_staff', 'date_joined')