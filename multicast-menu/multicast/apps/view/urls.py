from django.urls import path

from . import views

app_name = "view"

urlpatterns = [
    path('media/tunnel-files/<path:path>', views.serve_media_file, name='serve_media_file'),
    path("register/", views.register, name="register"),
    path("", views.index, name="index"),
    path("trending/", views.trending_index, name="trending_index"),
    path("editors_choice/", views.editors_choice_index, name="editors_choice_index"),
    path("liked/", views.liked_index, name="liked_index"),
    path("detail/<int:stream_id>/", views.detail, name="detail"),
    path("detail/open/<int:stream_id>/", views.open_file, name="open"),
    path("detail/watch/<int:stream_id>/", views.watch, name="watch"),
    path("detail/report/<int:stream_id>/", views.report, name="report"),
    path("description/upvote/<int:description_id>/", views.upvote_description, name="upvote_description"),
    path("description/downvote/<int:description_id>/", views.downvote_description, name="downvote_description"),
    path("description/submit/<int:stream_id>/", views.submit_description, name="submit_description"),
    path("broken/", views.broken_index, name="broken_index"),
    path("broken/detail/<int:stream_id>/", views.broken_detail, name="broken_detail"),
    path("broken/clear/<int:stream_id>/", views.broken_clear, name="broken_clear"),
    path("detail/set_editors_choice/<int:stream_id>/", views.set_editors_choice, name="set_editors_choice"),
    path("detail/like_stream/<int:stream_id>/", views.like_stream, name="like_stream"),
    path("detail/remove_like_from_stream/<int:stream_id>/", views.remove_like_from_stream, name="remove_like_from_stream"),
    path('check_stream_status/<int:stream_id>/', views.check_stream_status, name='check_stream_status'),
]
