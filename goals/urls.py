from django.urls import path

from . import views

app_name = 'goals'
urlpatterns = [
    path('', views.index, name='index'),
#    path('<int:goal_id>/', views.detail, name='detail'),
]
