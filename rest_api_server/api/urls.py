from django.urls import path
from .views.file_views import FileUploadView
from .views.users import GetAllUsers

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload_file'),
    path('users/', GetAllUsers.as_view(), name='get_all_users'),
]