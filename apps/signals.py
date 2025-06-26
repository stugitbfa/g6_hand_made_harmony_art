from notifications.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from notifications.models import Notification  

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance, message="Welcome to our platform!")
