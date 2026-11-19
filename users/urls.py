from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('registration/', views.RegistrationUserView.as_view(), name='registration'),
    path('confirm/<str:token>/', views.ConfirmEmailView.as_view(), name='confirm_email'),
    path('email-sent/', views.EmailSentView.as_view(), name='email_sent'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path('user_block/<int:pk>/', views.UserBlockView.as_view(), name='user_block'),
]