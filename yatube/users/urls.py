from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('password-change/', PasswordChangeView.as_view(
         template_name='users/password_change_form.html'),
         name='password-change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
         template_name='users/password_change_done.html'),
         name='password-change-done'),
    path('password-reset/', PasswordResetView.as_view(
         template_name='users/password_reset_form.html'),
         name='password-reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
         template_name='users/password_reset_done.html')),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html')),
    path('reset/done/', PasswordResetCompleteView.as_view(
         template_name='users/password_reset_complete.html')),
]