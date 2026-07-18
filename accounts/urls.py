from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('cart/', views.cart_view, name='cart_view'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)