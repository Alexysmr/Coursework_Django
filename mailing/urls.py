
from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # Сообщения
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('message/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('message/<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_confirm_delete'),
    # Рассылки
    path('mailing/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing/<int:pk>/send', views.MailingSendView.as_view(), name='mailing_send'),
    path('mailing/<int:pk>/stop', views.MailingStopView.as_view(), name='mailing_stop'),
]
