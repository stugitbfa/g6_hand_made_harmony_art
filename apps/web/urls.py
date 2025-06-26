from django.urls import path
from .views import *
from django.urls import include, path
from . import views
from django.urls import path
from .views import artist_profile_view


urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('email_verify/', email_verify, name='email_verify'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('logout/', logout, name='logout'),
    path('home/', home, name='home'),
    path('search/', search, name='search'),
    path('artist/<uuid:artist_id>/', view_profile, name='view_profile'),
    path('artist/<uuid:artist_id>/follow/', toggle_follow, name='toggle_follow'),
    path('posts/', posts, name='posts'),
    path('post/<uuid:post_id>/', post_detail, name='post_detail'),
    path('like/<uuid:post_id>/', toggle_like, name='toggle_like'),
    path('comment/<uuid:post_id>/', add_comment, name='add_comment'),
    path('edit-post/<uuid:post_id>/', edit_post, name='edit_post'),
    path('notification/', notification, name='notification'),
    path('profile/', profile, name='profile'),
    path('', views.home, name='home'), 
    path('artist/<int:artist_id>/', artist_profile_view, name='artist_profile'),
]