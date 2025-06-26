from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, ArtistProfile, Post


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile', 'is_active')
    search_fields = ('username', 'email', 'mobile')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    ordering = ('username',)


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('artist', 'gender', 'date_of_birth', 'profile_image_preview')
    readonly_fields = ('profile_image_preview',)
    search_fields = ('artist__username',)
    list_filter = ('gender',)

    def profile_image_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="60" height="60" style="border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
        return "(No Image)"
    profile_image_preview.short_description = 'Profile Picture'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('artist', 'caption_short', 'likes', 'comments', 'is_public', 'post_image_preview')
    search_fields = ('artist__username', 'caption')
    list_filter = ('is_public', 'artist')
    readonly_fields = ('post_image_preview',)
    ordering = ('-create_at',)

    def caption_short(self, obj):
        return (obj.caption[:30] + '...') if obj.caption and len(obj.caption) > 30 else obj.caption
    caption_short.short_description = 'Caption'

    def post_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "(No Image)"
    post_image_preview.short_description = 'Post Image'
