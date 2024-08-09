from django.db import models

from ..view.models import Stream


# Extra Models for Administrative Tracking
class FailedQuery(models.Model):
    id = models.AutoField(primary_key=True)

    ip = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Failed on {} at {} UTC".format(self.ip, self.time)


class Translator(models.Model):
    id = models.AutoField(primary_key=True)

    uid = models.CharField(max_length=100)
    name = models.CharField(max_length=40)

    allowed_inside = models.BooleanField(default=False)

    def __str__(self):
        return "Translator with UID {}".format(self.uid)


# METHOD 1: Submission via automated scraping
class ScrapingSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    
    # Administration
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name="scraping")
    time = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Scraping at {} (Stream ID: {})".format(self.time, self.stream.id)


# METHOD 2: Submission via a manual report
class ManualSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    # Administration
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name="manual")
    time = models.DateTimeField(auto_now=True)

    # Celery
    active = models.BooleanField()
    celery_id = models.CharField(max_length=100, blank=True, null=True)

    # Management
    error_msg = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)


    def __str__(self):
        return "Manual at {} (Stream ID: {})".format(self.time, self.stream.id)
    

# METHOD 3: Submission via a file upload
class UploadSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    # Administration
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name="upload")
    time = models.DateTimeField(auto_now=True)

    # Celery
    active = models.BooleanField()
    celery_id = models.CharField(max_length=100, blank=True, null=True)
    stream_pid = models.IntegerField(blank=True, null=True)

    # Management
    access_code = models.CharField(max_length=100)
    uploaded_file = models.CharField(max_length=100)
    matched = models.BooleanField(default=False)


    def __str__(self):
        return "Upload at {} (Stream ID: {})".format(self.time, self.stream.id)

    
# METHOD 4: Submission via the API
class APISubmission(models.Model):
    id = models.AutoField(primary_key=True)

    # Administration
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name="api")
    time = models.DateTimeField(auto_now=True)
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE)

    # Management
    access_code = models.CharField(max_length=40)


    def __str__(self):
        return "API at {} (Stream ID: {})".format(self.time, self.stream.id)
