from django.db import models
from django.conf import settings

# Create your models here.

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
