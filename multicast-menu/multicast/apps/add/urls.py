from django.urls import path

from . import views


app_name = "add"

urlpatterns = [
    path("", views.index, name="index"),
    path("manual/", views.add_manual, name="add_manual"),
    path("upload/", views.add_upload, name="add_upload"),
]
