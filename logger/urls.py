from django.urls import path

from . import views

app_name = 'logger'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:workout_id>/', views.detail, name='detail'),
    path('delete/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('delete/<str:type>/<int:activity_id>/', views.delete_activity, name='delete_activity'),
]
