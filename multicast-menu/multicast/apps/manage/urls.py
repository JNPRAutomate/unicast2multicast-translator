from django.urls import path

from . import views

app_name = "manage"

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<int:stream_id>", views.edit, name="edit"),
    path("remove/<int:stream_id>", views.remove, name="remove"),
    path("retry_verification/<int:stream_id>", views.retry_verification, name="retry_verification"),
]
