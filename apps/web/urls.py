from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('index/', index, name='index'),
    path('register/', register, name='register'),
    path('email-verify/', email_verify, name='email_verify'),
]