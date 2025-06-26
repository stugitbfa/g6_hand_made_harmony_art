from django import forms
from apps.web.models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption', 'is_public']
