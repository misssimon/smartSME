from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

     # Your custom accounts URLs
    path('accounts/', include('accounts.urls')),

    # Allauth URLs (Social login, password reset, etc.)
    path('accounts/', include('allauth.urls')),

    # WebAuthn / Passkeys URLs (Required for django-otp-webauthn)
    path('webauthn/', include('django_otp_webauthn.urls', namespace='otp_webauthn')),

    path('dashboard/', include('dashboard.urls')),
    path('checkout/', include('checkout.urls')),
    path('payment/', include('payment.urls')),

    # Redirect root to login
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)