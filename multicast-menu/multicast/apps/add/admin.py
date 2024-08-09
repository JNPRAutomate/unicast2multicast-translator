from django.contrib import admin

from .models import APISubmission, FailedQuery, ManualSubmission, ScrapingSubmission, Translator, UploadSubmission


admin.site.register(APISubmission)
admin.site.register(FailedQuery)
admin.site.register(ManualSubmission)
admin.site.register(ScrapingSubmission)
admin.site.register(Translator)
admin.site.register(UploadSubmission)
