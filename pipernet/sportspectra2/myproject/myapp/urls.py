from django.urls import path
from .views import AuthUserListCreate, AuthUserDetail, LivestreamListCreate, LivestreamDetail, signup, login, start_web_stream, stop_web_stream, stream_video_url, upload_video, current_user

urlpatterns = [
    path('auth_users/', AuthUserListCreate.as_view(), name='auth_user_list_create'),
    path('auth_users/<int:pk>/', AuthUserDetail.as_view(), name='auth_user_detail'),
    path('livestreams/', LivestreamListCreate.as_view(), name='livestream_list_create'),
    path('livestreams/<int:pk>/', LivestreamDetail.as_view(), name='livestream_detail'),
    path('signup/', signup, name='signup'), 
    path('login/', login, name='login'),  
    path('upload_video/', upload_video, name='upload_video'),  # Added upload_video endpoint
    path('users/', AuthUserListCreate.as_view(), name='user_list'),
    path('current_user/', current_user, name='current_user'),  
    path('start_web_stream/', start_web_stream, name='start_web_stream'),
    path('stop_web_stream/', stop_web_stream, name='stop_web_stream'),
    path('stream_video_url/', stream_video_url, name='stream_video_url'),
]