from django.db import models

class AuthUser(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Stream(models.Model):
    channelId = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    image = models.URLField(blank=True, null=True)
    viewers = models.IntegerField()
    organization = models.CharField(max_length=255)
    liked = models.BooleanField(default=False)
    totalLikes = models.IntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    
    # Additional fields for manual reporting
    source_ip = models.CharField(max_length=255, blank=True, null=True)
    group_ip = models.CharField(max_length=255, blank=True, null=True)
    udp_port = models.CharField(max_length=255, blank=True, null=True)
    amt_relay = models.CharField(max_length=255, blank=True, null=True)
    
    def delete(self, *args, **kwargs):
        if self.video_url and self.video_url.startswith('/media/'):
            if default_storage.exists(self.video_url):
                default_storage.delete(self.video_url)
        super(Stream, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title