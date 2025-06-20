from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings

from functools import wraps

from .models import *
from .helpers import *

import random

# Create your views here.
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'artist_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper 

def login(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        password_ = request.POST['password']

        if not Artist.objects.filter(email=email_).exists():
            print("Email does't Exist")
            return redirect('login')

        get_artist = Artist.objects.get(email=email_)

        if not get_artist.is_active:
            print("you account is deactivate please contact to artist care.")
            return redirect('login')

        is_valid = check_password(password_, get_artist.password)
        if not is_valid:
            print("Email or paddword not match.")
            return redirect('login')
        
        request.session['artist_id'] = str(get_artist.aid)
        return redirect('index')
        
    return render(request, 'web/login.html' \
    '')

def register(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        password_ = request.POST['password']
        confirm_password_ = request.POST['confirm_password']

        if not is_email_verified(email_):
            print("Invaild Email")
            return redirect('register')
        
        if Artist.objects.filter(email=email_).exists():
            print("Email already exist")
            return redirect('register')
        
        if not is_valid_mobile_number(mobile_):
            print("Invaild Mobile number")
            return redirect('register')
        
        if password_ != confirm_password_:
            print("Password and confirm password does't match.") 
            return redirect('register')
    
        
        if not validate_password(password_)[0]:
            print(validate_password(password_)[1])
            return redirect('register')
        
        new_artist = Artist.objects.create(
            email=email_,
            mobile=mobile_,
            password=make_password(password_)
        )
        new_artist.save()
        otp = random.randint(111111, 999999)
        new_artist.otp = otp
        new_artist.save()
        subject = "Confirm Your Account | Hand made harmony arts"
        message = f"""
        Dear User,

        Thank you for registering with Hand made harmony arts.

        Your One-Time Password (OTP) for email verification is: {otp}

        Please enter this OTP in the app/website to complete your email verification process. 

        If you did not request this, please ignore this email.

        Best regards,  
        Team Hand made harmony arts
        """

        send_mail(subject, message, settings.EMAIL_HOST_USER, [f"{email_}"])
        print("Your registration successfully done. please check you rmail for mail conformation")
        context = {
            'email': email_
        }
        return render(request, 'web/email_verify.html', context)

    return render(request, 'web/register.html')

def email_verify(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']

        if not Artist.objects.filter(email=email_).exists():
            print("Email does't Exixt")
            return render(request, 'web/email_verify.html', {'email': email_})
        
        get_artist = Artist.objects.get(email=email_)

        if otp_ != get_artist.otp:
            print("Invalid OTP")
            return render(request, 'web/email_verify.html', {'email': email_})
        
        get_artist.is_active = True
        get_artist.save()
        return redirect('login')

    return render(request, 'web/email_verify.html')
def index(request):
    return render(request,'web/index.html')