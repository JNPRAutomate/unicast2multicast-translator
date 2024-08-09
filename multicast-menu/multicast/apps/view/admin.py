from django.contrib import admin

from .models import Category, Description, Stream, TrendingStream, Tunnel

admin.site.register(Category)
admin.site.register(Description)
admin.site.register(Stream)
admin.site.register(TrendingStream)
admin.site.register(Tunnel)
