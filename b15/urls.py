from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from main import views
from . import settings

urlpatterns = [
    path('', views.index, name='home'),
    path('logout/', views.logout, name='logout'),
    path('log/', include('logger.urls')),
    path('goals/', include('goals.urls')),
    path('friends/', include('social.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('planner/', include('planner.urls')),

    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

#    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
