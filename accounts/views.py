from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.utils import timezone
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import Profile
from django.db import IntegrityError


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()

                # Set role on profile
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile.objects.create(user=user)
                
                profile.role = form.cleaned_data.get('role', 'institutional_buyer')
                profile.save()

                # === Send Welcome Email ===
                try:
                    html_message = render_to_string('accounts/email/account_created.html', {
                        'user': user,
                        'role': profile.get_role_display(),
                        'site_name': 'smartSME',
                    })
                    email = EmailMessage(
                        subject='Welcome to smartSME! Your Account Has Been Created',
                        body=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email],
                    )
                    email.content_subtype = 'html'
                    email.send(fail_silently=True)
                    print(f"✅ Welcome email sent to {user.email}")
                except Exception as e:
                    print(f"⚠️ Failed to send welcome email: {e}")

                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('accounts:login')

            except IntegrityError:
                messages.error(request, 'Username already exists. Please choose a different username.')
            except Exception as e:
                messages.error(request, 'Something went wrong. Please try again.')
                print(f"Registration error: {e}")

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # === Login Notification Email ===
            try:
                html_message = render_to_string('accounts/email/login_notification.html', {
                    'user': user,
                    'login_time': timezone.now(),
                    'site_name': 'smartSME',
                })
                email = EmailMessage(
                    subject='New Login Detected - smartSME',
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email.content_subtype = 'html'
                email.send(fail_silently=True)
            except Exception as e:
                print(f"⚠️ Login notification email failed: {e}")

            # Role-based redirect
            try:
                profile = user.profile
                if profile.role == 'farmer':
                    return redirect('dashboard:farmer_dashboard')
                else:
                    return redirect('dashboard:buyer_dashboard')
            except Profile.DoesNotExist:
                Profile.objects.create(user=user, role='institutional_buyer')
                return redirect('dashboard:buyer_dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def home(request):
    """Redirect users based on their role"""
    try:
        profile = request.user.profile
        if profile.role == 'farmer':
            return redirect('dashboard:farmer_dashboard')
        else:
            return redirect('dashboard:buyer_dashboard')
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user, role='institutional_buyer')
        return redirect('dashboard:buyer_dashboard')


@login_required
def cart_view(request):
    return render(request, 'accounts/cart.html')