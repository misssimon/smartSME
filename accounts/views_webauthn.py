# ====================== BIOMETRIC (WEBAUTHN) VIEWS ======================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_otp_webauthn.views import (
    BeginCredentialRegistrationView,
    CompleteCredentialRegistrationView,
    BeginCredentialAuthenticationView,
    CompleteCredentialAuthenticationView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnLoginBeginView(BeginCredentialAuthenticationView):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnLoginCompleteView(CompleteCredentialAuthenticationView):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnRegisterBeginView(BeginCredentialRegistrationView):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnRegisterCompleteView(CompleteCredentialRegistrationView):
    pass


# For backwards compatibility with your urls.py
webauthn_login_begin = WebAuthnLoginBeginView.as_view()
webauthn_login_complete = WebAuthnLoginCompleteView.as_view()
webauthn_register_begin = WebAuthnRegisterBeginView.as_view()
webauthn_register_complete = WebAuthnRegisterCompleteView.as_view()