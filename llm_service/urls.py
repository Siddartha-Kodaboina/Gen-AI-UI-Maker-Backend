from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_code, name='generate_code'),
    path('files/', views.manage_files, name='manage_files'),
    path('preview/<str:filename>', views.preview_file, name='preview_file'),
]