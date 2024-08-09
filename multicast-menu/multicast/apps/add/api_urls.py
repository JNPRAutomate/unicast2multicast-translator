from django.urls import path

from . import api_views


app_name = "api"

urlpatterns = [
    path("add/", api_views.SubmissionAdd.as_view(), name="add_api"),
    path("remove/", api_views.SubmissionRemove.as_view(), name="remove_api"),
]
