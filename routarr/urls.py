from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.upload_torrent, name='upload_torrent'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-tracker/', views.add_tracker, name='add_tracker'),
    path('admin/', admin.site.urls),
]
