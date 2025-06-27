from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.upload_torrent, name='upload_torrent'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-tracker/', views.add_tracker, name='add_tracker'),
    path('list-directories/', views.list_directories, name='list_directories'),
    path('admin/', admin.site.urls),
]
