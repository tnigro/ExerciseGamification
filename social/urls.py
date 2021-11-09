from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path('', views.index, name='index'),
    path('users/<str:username>/', views.detail, name='detail'), # user profile
    path('search/', views.search, name='search'),
    path('unfriend/<str:username>', views.unfriend, name='unfriend'),
    path('posts/<int:workout_id>', views.post_detail, name='post'),
    path('delete/<int:comment_id>', views.delete_comment, name='delete_comment'),
]
