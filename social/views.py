from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.conf import settings # Import the settings module

# Models and Forms
from .models import Post, Location, Message, Profile
from .forms import PostForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm

# Corrected Import for form widgets
from django.forms import PasswordInput

# Authentication and Password Validation/Reset
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password

# Other necessary imports
import random
from django.core.mail import send_mail
from datetime import datetime, timedelta


def home_view(request):
    """
    Handles the main social feed with correct filtering logic.
    """
    now = timezone.now()
    location_filter_id = request.GET.get('location')

    base_queryset = Post.objects.filter(is_active=True, expires_at__gt=now)

    if location_filter_id:
        posts = base_queryset.filter(location_id=location_filter_id)
    else:
        posts = base_queryset.filter(
            Q(location__isnull=True) | Q(is_location_specific=False)
        )

    posts = posts.order_by('-created_at')
    locations = Location.objects.filter(city="Lucknow").order_by('name')

    context = {
        'posts': posts,
        'locations': locations,
        'current_location_id': location_filter_id,
    }
    return render(request, 'social/home.html', context)


def register_request_view(request):
    """Handles Step 1 of registration: getting username/email and sending OTP."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken. Please choose another.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            otp = random.randint(100000, 999999)

            request.session['reg_username'] = username
            request.session['reg_email'] = email
            request.session['reg_otp'] = otp
            request.session['reg_otp_expires_at'] = (datetime.now() + timedelta(minutes=10)).isoformat()

            send_mail(
                'Verify your email for upzunction',
                f'Your verification OTP is: {otp}\nIt will expire in 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,  # <-- THE FIX: Use the verified email
                [email],
                fail_silently=False,
            )
            messages.info(request, 'A verification OTP has been sent to your email.')
            return redirect('register_verify')

    return render(request, 'registration/register_request.html')


def register_verify_view(request):
    """Handles Step 2 of registration: verifying OTP and setting password."""
    username = request.session.get('reg_username')
    email = request.session.get('reg_email')
    session_otp = request.session.get('reg_otp')
    otp_expires_at = request.session.get('reg_otp_expires_at')

    if not all([username, email, session_otp, otp_expires_at]):
        messages.error(request, 'Your registration session has expired. Please start over.')
        return redirect('register_request')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if datetime.fromisoformat(otp_expires_at) < datetime.now():
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('register_request')

        if not (entered_otp and session_otp and int(entered_otp) == session_otp):
            messages.error(request, 'Invalid OTP. Please try again.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password)
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)

                for key in list(request.session.keys()):
                    if key.startswith('reg_'):
                        del request.session[key]

                messages.success(request, 'Registration successful! You are now logged in.')
                return redirect('home')

            except Exception as e:
                messages.error(request, f'Password is not strong enough: {e}')

    return render(request, 'registration/register_verify.html', {'email': email})


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f"Your post '{post.title}' has been created!")
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'social/create_post.html', {'form': form})


@login_required
def dashboard_view(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    received_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-sent_at')

    context = {
        'user_posts': user_posts,
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'social/dashboard.html', context)


@login_required
def deactivate_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.is_active = False
        post.save()
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def send_message_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        if post.author == request.user:
            messages.error(request, "You cannot send a message to yourself.")
            return redirect('home')

        message_body = request.POST.get('message_body')
        sender_phone = request.POST.get('sender_phone')

        if message_body:
            Message.objects.create(
                post=post,
                sender=request.user,
                recipient=post.author,
                body=message_body,
                sender_phone=sender_phone
            )
            messages.success(request, "Your message has been sent successfully!")
    return redirect('home')


@login_required
def approve_message_view(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if request.method == 'POST':
        message.is_approved = True
        recipient_phone = request.POST.get('recipient_phone')
        if recipient_phone:
            message.recipient_phone_on_approval = recipient_phone
        message.save()
        messages.success(request, f"You have approved the offer from {message.sender.username}!")
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Your post has been updated successfully!")
            return redirect('dashboard')
    else:
        form = PostForm(instance=post)
    return render(request, 'social/edit_post.html', {'form': form})


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f"The post '{post_title}' has been deleted.")
        return redirect('dashboard')
    return render(request, 'social/delete_confirmation.html', {'post': post})


@login_required
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'social/profile.html', context)


def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['otp_expires_at'] = (datetime.now() + timedelta(minutes=5)).isoformat()
            send_mail(
                'Your Password Reset OTP for upzunction',
                f'Your OTP is: {otp}\nIt will expire in 5 minutes.',
                settings.DEFAULT_FROM_EMAIL,  # <-- THE FIX: Use the verified email
                [email],
                fail_silently=False,
            )
            messages.info(request, 'An OTP has been sent to your email.')
            return redirect('password_reset_otp')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
    return render(request, 'registration/password_reset_request.html')


def password_reset_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('reset_otp')
        otp_expires_at = request.session.get('otp_expires_at')

        if otp_expires_at is None or datetime.fromisoformat(otp_expires_at) < datetime.now():
            messages.error(request, 'OTP has expired. Please request a new one.')
            if 'reset_otp' in request.session: del request.session['reset_otp']
            if 'reset_email' in request.session: del request.session['reset_email']
            if 'otp_expires_at' in request.session: del request.session['otp_expires_at']
            return redirect('password_reset_request')

        if otp_entered and otp_session and int(otp_entered) == otp_session:
            request.session['otp_verified'] = True
            return redirect('password_reset_new')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'registration/password_reset_otp.html')


def password_reset_new_password_view(request):
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify your OTP first.')
        return redirect('password_reset_otp')

    email = request.session.get('reset_email')
    user = User.objects.get(email=email)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            if 'reset_otp' in request.session: del request.session['reset_otp']
            if 'reset_email' in request.session: del request.session['reset_email']
            if 'otp_expires_at' in request.session: del request.session['otp_expires_at']
            if 'otp_verified' in request.session: del request.session['otp_verified']
            messages.success(request, 'Your password has been reset successfully. Please log in.')
            return redirect('login')
    else:
        form = SetPasswordForm(user)

    return render(request, 'registration/password_reset_new.html', {'form': form})


def terms_of_service_view(request):
    return render(request, 'social/terms_of_service.html')


def privacy_policy_view(request):
    return render(request, 'social/privacy_policy.html')

