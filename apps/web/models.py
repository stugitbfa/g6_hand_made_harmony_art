from django.db import models

import uuid

# Create your models here.
class BaseClass(models.Model):
    aid = models.UUIDField(primary_key=True, blank=False, null=False, default=uuid.uuid4)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Artist(BaseClass):
    email = models.EmailField(max_length=255, blank=False, null=False)
    mobile = models.CharField(max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    otp = models.CharField(max_length=20, blank=False, null=False, default="112233")
    is_active = models.BooleanField(default=False)