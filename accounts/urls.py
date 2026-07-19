from django.urls import path
from . import views
from .views_webauthn import (          # ← Import from here
    webauthn_login_begin,
    webauthn_login_complete,
    webauthn_register_begin,
    webauthn_register_complete,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('cart/', views.cart_view, name='cart_view'),

    # Biometric (WebAuthn) URLs
    path('webauthn/login/begin/', webauthn_login_begin, name='webauthn_login_begin'),
    path('webauthn/login/complete/', webauthn_login_complete, name='webauthn_login_complete'),
    path('webauthn/register/begin/', webauthn_register_begin, name='webauthn_register_begin'),
    path('webauthn/register/complete/', webauthn_register_complete, name='webauthn_register_complete'),
]

# Remove the old import from views_webauthn at the top if it's still there