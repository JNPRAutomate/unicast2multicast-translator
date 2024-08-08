from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Optional: Keep if you want to use the admin interface
    path('api/', include('myapp.urls')),  # This includes the URLs defined in myapp/urls.py
    path('', include('myapp.urls')),  # Other endpoints
]