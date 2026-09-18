from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    path('', views.album_list, name='list'),
    path('create/', views.album_create, name='create'),
    path('<int:pk>/', views.album_detail, name='detail'),
    path('<int:pk>/edit/', views.album_edit, name='edit'),
    path('<int:pk>/delete/', views.album_delete, name='delete'),
     path('api/list/', views.api_album_list, name='api_list'),
    path('api/toggle/', views.api_toggle_post, name='api_toggle'),
    path('api/create/', views.api_create_album, name='api_create'),
]