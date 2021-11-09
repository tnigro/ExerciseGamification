from django.conf.urls import url
from . import views

app_name = 'planner'
urlpatterns = [
    url('', views.CalendarView.as_view(), name='calendar'),
]