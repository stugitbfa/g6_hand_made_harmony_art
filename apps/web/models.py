from django.db import models
from django.db.models import Index
from django.contrib.contenttypes.models import ContentType
from django.db import models
import uuid
import os
import datetime


class BaseClass(models.Model):
    actor_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, related_name='+')
    actor_object_id = models.UUIDField()
    
    target_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, related_name='+')
    target_object_id = models.UUIDField()
    
    action_object_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    action_object_object_id = models.UUIDField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['actor_object_id', 'actor_content_type']),
            models.Index(fields=['target_object_id', 'target_content_type']),
            models.Index(fields=['action_object_object_id', 'action_object_content_type']),
        ]

class BaseClass(models.Model):
    id = models.UUIDField(primary_key=True, blank=False, null=False, default=uuid.uuid4)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Artist(BaseClass):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    mobile = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    otp = models.CharField(max_length=20, default="112233")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username


def artist_profile_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.artist.id}.{ext}"
    return os.path.join('artist_profiles', filename)


class ArtistProfile(BaseClass):
    artist = models.OneToOneField('Artist', on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to=artist_profile_upload_path,
        default='Default_images/artist_default_profile.png',
        null=True, blank=True
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(default=datetime.date(2000, 1, 1), null=True, blank=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.artist.username}"


class Follow(BaseClass):
    follower = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Post(BaseClass):
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='artist_posts/')
    caption = models.TextField(blank=True, null=True)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"Post by {self.artist.username} at {self.create_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def likes_count(self):
        return self.likes_set.count()

    @property
    def comments_count(self):
        return self.comments_set.count()


class PostLike(BaseClass):
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='liked_posts')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes_set')

    def __str__(self):
        return f"{self.artist.username} liked Post {self.post.id}"


class PostComment(BaseClass):
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments_set')
    text = models.TextField()

    def __str__(self):
        return f"{self.artist.username} commented on Post {self.post.id}"


class Notification(BaseClass):
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_by = models.ForeignKey('Artist', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')

    NOTIFICATION_TYPE_CHOICES = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('general', 'General'),
        
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='general')

    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('PostComment', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.artist.username}: {self.message[:30]}"
