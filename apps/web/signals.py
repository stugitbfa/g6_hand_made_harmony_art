from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.web.models import *

@receiver(post_save, sender=Artist)
def create_artist_profile(sender, instance, created, **kwargs):
    if created:
        ArtistProfile.objects.create(artist=instance)

@receiver(pre_save, sender=ArtistProfile)
def auto_delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_file = ArtistProfile.objects.get(pk=instance.pk).profile_picture
    except ArtistProfile.DoesNotExist:
        return

    new_file = instance.profile_picture
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path) and 'artist_default_profile.png' not in old_file.path:
            os.remove(old_file.path)
