from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Регистрация
    path('register/', views.register, name='register'),

    # Вход / выход (встроенные view Django)
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='pages:home'),
        name='logout',
    ),

    # Профиль
    path('profile/<str:username>/', views.profile, name='profile'),
]