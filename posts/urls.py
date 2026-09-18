from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('upload/', views.post_create, name='create'),
    path('search/', views.search, name='search'),
    path('comments/<int:pk>/like/', views.toggle_comment_like, name='comment_like'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/edit/', views.post_edit, name='edit'),          
    path('<int:pk>/delete/', views.post_delete, name='delete'),    
    path('<int:pk>/like/', views.toggle_post_like, name='toggle_like'),
    path('<int:pk>/comment/', views.comment_create, name='comment_create'),
]