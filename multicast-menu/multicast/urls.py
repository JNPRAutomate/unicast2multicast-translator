from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from multicast.apps.view.forms import CustomLoginForm

urlpatterns = ([
    path("login/", LoginView.as_view(authentication_form=CustomLoginForm), name="login"),
    path("", include("django.contrib.auth.urls")),
    path("", include("multicast.apps.view.urls", namespace="view")),
    path("add/", include("multicast.apps.add.urls", namespace="add")),
    path("admin/", admin.site.urls),
    path("api/", include("multicast.apps.add.api_urls", namespace="api")),
    path("manage/", include("multicast.apps.manage.urls", namespace="manage")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
