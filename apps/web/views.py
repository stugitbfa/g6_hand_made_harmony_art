from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from Apps.artist.models import Artist, Notification 

from .helpers import *
from .models import *
from .forms import *

from datetime import timedelta
from functools import wraps

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
            messages.error(request, "Email doesn't exist.")
            return redirect('login')

        get_artist = Artist.objects.get(email=email_)

        if not get_artist.is_active:
            messages.error(request, "Your account is deactivated. Please contact ArtInsta support.")
            return redirect('login')

        is_valid = check_password(password_, get_artist.password)
        if not is_valid:
            messages.error(request, "Email or password do not match.")
            return redirect('login')

        request.session['artist_id'] = str(get_artist.id)
        messages.success(request, "Logged in successfully.")
        return redirect('home')

    return render(request, 'web/login.html')

def register(request):
    if request.method == 'POST':
        username_ = request.POST['username']
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        password_ = request.POST['password']
        confirm_password_ = request.POST['confirm_password']

        if Artist.objects.filter(username=username_).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if not is_email_verified(email_):
            messages.error(request, "Invalid email address.")
            return redirect('register')

        if Artist.objects.filter(email=email_).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if not is_valid_mobile_number(mobile_):
            messages.error(request, "Invalid mobile number.")
            return redirect('register')

        if password_ != confirm_password_:
            messages.error(request, "Password and confirm password do not match.")
            return redirect('register')

        if not validate_password(password_)[0]:
            messages.error(request, validate_password(password_)[1])
            return redirect('register')

        new_artist = Artist.objects.create(
            username=username_,
            email=email_,
            mobile=mobile_,
            password=make_password(password_)
        )
        otp = random.randint(111111, 999999)
        new_artist.otp = otp
        new_artist.save()

        subject = "Confirm Your Account | ArtInsta"
        message = f"""
        Dear User,

        Thank you for registering with ArtInsta.

        Your One-Time Password (OTP) for email verification is: {otp}

        Please enter this OTP in the app/website to complete your email verification process. 

        If you did not request this, please ignore this email.

        Best regards,  
        Team ArtInsta
        """
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email_])

        messages.success(request, "Registration successful. Please check your email to verify your account.")
        return render(request, 'web/email_verify.html', {'email': email_})

    return render(request, 'web/register.html')

def email_verify(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']

        if not Artist.objects.filter(email=email_).exists():
            messages.error(request, "Email doesn't exist.")
            return render(request, 'web/email_verify.html', {'email': email_})

        get_artist = Artist.objects.get(email=email_)

        if otp_ != get_artist.otp:
            messages.error(request, "Invalid OTP.")
            return render(request, 'web/email_verify.html', {'email': email_})

        get_artist.is_active = True
        get_artist.save()
        messages.success(request, "Email verified successfully. You can now log in.")
        return redirect('login')

    return render(request, 'web/email_verify.html')

def forgot_password(request):
    return render(request, 'web/forgot_password.html')

@login_required
def home(request):
    artist = Artist.objects.get(id=request.session['artist_id'])

    # Get artists I follow
    following_list = Artist.objects.filter(followers__follower=artist)

    # 48 hours ago from now
    time_threshold = timezone.now() - timedelta(hours=48)

    # Get posts from me or followed artists, created within the last 48 hours
    posts = Post.objects.filter(
        models.Q(artist=artist) | models.Q(artist__in=following_list),
        is_public=True,
        create_at__gte=time_threshold  # CREATED in the last 48 hours
    ).order_by('-create_at')

    # Followers = people who follow me
    followers = Artist.objects.filter(following__following=artist)

    return render(request, 'web/home.html', {
        'followers': followers,
        'following_list': following_list,
        'posts': posts
    })


@login_required
def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Artist.objects.filter(
            Q(username__icontains=query) | Q(mobile__icontains=query),
            is_active=True
        )

    context = {
        'results': results, 
        'query': query
    }
    return render(request, 'web/search.html', context)

@login_required
def view_profile(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    artist_profile = get_object_or_404(ArtistProfile, artist_id=artist_id)

    viewer_id = request.session.get('artist_id')
    viewer = get_object_or_404(Artist, id=viewer_id)

    # Prevent viewing own profile via public view
    if viewer.id == artist.id:
        return redirect('profile')

    # Follow state
    is_following = Follow.objects.filter(follower=viewer, following=artist).exists()
    follower_count = artist.followers.count()
    following_count = artist.following.count()

    context = {
        'artist': artist,
        'artist_profile': artist_profile,
        'is_following': is_following,
        'follower_count': follower_count,
        'following_count': following_count
    }
    return render(request, 'web/view_profile.html', context)


@login_required
def toggle_follow(request, artist_id):
    follower = get_object_or_404(Artist, id=request.session['artist_id'])
    following = get_object_or_404(Artist, id=artist_id)

    if follower == following:
        messages.error(request, "You cannot follow yourself.")
    else:
        follow_obj, created = Follow.objects.get_or_create(follower=follower, following=following)
        if not created:
            follow_obj.delete()
            messages.info(request, "Unfollowed successfully.")
        else:
            messages.success(request, "Followed successfully.")

    return redirect('view_profile', artist_id=artist_id)


@login_required
def posts(request):
    artist_id = request.session.get('artist_id')  # Use .get() to avoid KeyError

    # Artist fetch & error handling
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        messages.error(request, "Artist not found.")
        return redirect('home')

    # Handle form submission
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.artist = artist
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('posts')  # Updated to stay on post page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()

    # All posts by this artist
    posts = Post.objects.filter(artist=artist).order_by('-create_at')

    context = {
        'form': form,
        'posts': posts,
        'artist': artist,
        'artist_id':artist_id
    }
    return render(request, 'web/posts.html', context)

@login_required
def post_detail(request, post_id):
    artist_id = request.session.get('artist_id')  # Assuming session-based login
    post = get_object_or_404(Post, id=post_id)

    liked = PostLike.objects.filter(post=post, artist_id=artist_id).exists()
    comments = post.comments_set.order_by('-create_at')  # Most recent first

    if request.method == 'POST':
        text = request.POST.get('comment')
        if text:
            PostComment.objects.create(artist_id=artist_id, post=post, text=text)
            return redirect('post_detail', post_id=post_id)

    context = {
        'post': post,
        'liked': liked,
        'comments': comments
    }
    return render(request, 'web/post_detail.html', context)


@login_required
def toggle_like(request, post_id):
    artist_id = request.session.get('artist_id')
    if not artist_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    artist = get_object_or_404(Artist, id=artist_id)
    post = get_object_or_404(Post, id=post_id)

    liked_obj = PostLike.objects.filter(artist=artist, post=post)
    if liked_obj.exists():
        liked_obj.delete()
        liked = False
    else:
        PostLike.objects.create(artist=artist, post=post)
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })

@require_POST
@login_required
def add_comment(request, post_id):
    artist_id = request.session.get('artist_id')
    if not artist_id:
        return redirect('login')

    post = get_object_or_404(Post, id=post_id)
    artist = get_object_or_404(Artist, id=artist_id)
    text = request.POST.get('text')

    if text.strip():
        PostComment.objects.create(artist=artist, post=post, text=text)

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, artist_id=request.session['artist_id'])

    if request.method == 'POST':
        post.caption = request.POST.get('caption', post.caption)
        post.is_public = True if request.POST.get('is_public') else False

        if 'image' in request.FILES:
            post.image = request.FILES['image']

        post.save()
        messages.success(request, "Post updated successfully!")
        return redirect('posts')  # replace with actual

    messages.error(request, "Invalid request.")
    return redirect('posts')


@login_required
def notification(request):
    return render(request, 'web/notification.html')

@login_required
def profile(request):
    artist = Artist.objects.get(id=request.session['artist_id'])

    # Get or create profile
    profile, _ = ArtistProfile.objects.get_or_create(artist=artist)

    if request.method == 'POST':
        # Update mobile number
        artist.mobile = request.POST.get('mobile')
        artist.save()

        # Update profile fields
        profile.gender = request.POST.get('gender')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.bio = request.POST.get('bio')

        if 'profile_picture' in request.FILES:
            # Remove old image if it's not the default
            if profile.profile_picture and profile.profile_picture.name != 'Default_images/artist_default_profile.png':
                if os.path.isfile(profile.profile_picture.path):
                    os.remove(profile.profile_picture.path)

            # Assign new image
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    
    follower_count = Follow.objects.filter(following=artist).count()
    following_count = Follow.objects.filter(follower=artist).count()

    return render(request, 'web/profile.html', {
        'artist': artist,
        'profile': profile,
        'follower_count': follower_count,
        'following_count': following_count
    })

@login_required
def logout(request):
    del request.session['artist_id']
    print("Now, you are logged Out.")
    return redirect('login')


from django.shortcuts import render, get_object_or_404
from Apps.artist.models import Artist, Notification  # adjust if needed

def artist_profile_view(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    artist_profile = artist.profile
    follower_count = artist.followers.count()
    following_count = artist.following.count()
    is_following = request.user in artist.followers.all()

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'web/artist_profile.html', {
        'artist': artist,
        'artist_profile': artist_profile,
        'follower_count': follower_count,
        'following_count': following_count,
        'is_following': is_following,
        'notifications': notifications,
    })
