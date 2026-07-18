from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
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

            # Send welcome email
            try:
                html_message = render_to_string('accounts/email/account_created.html', {
                    'user': user,
                    'role': profile.get_role_display(),
                })
                email = EmailMessage(
                    'Welcome to ShopEase!',
                    html_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email.content_subtype = 'html'
                email.send(fail_silently=True)
            except Exception:
                pass

            messages.success(request, 'Account created successfully! Please log in.')
            return render(request, 'accounts/register.html', {
                'form': RegisterForm(),
                'redirect_to_login': True
            })
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Role-based redirect to new dashboard app
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