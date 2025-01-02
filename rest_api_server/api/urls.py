from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.users import GetAllUsers

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload_file'),
    path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
    path('users/', GetAllUsers.as_view(), name='get_all_users'),
]