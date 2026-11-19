from django.db import models
from django.conf import settings

from clients.models import Client

NULLABLE = {'blank': True, 'null': True}


class Message(models.Model):
    """Сообщения"""

    title = models.CharField(max_length=150)
    message_body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='владелец'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}. {self.message_body[:50]}...'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'


class Mailing(models.Model):
    """Рассылки"""

    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='владелец'
    )
    start_time_mailing = models.DateTimeField(verbose_name='дата и время начала')
    stop_time_mailing = models.DateTimeField(verbose_name='дата и время окончания')
    status_sending = models.CharField(
        max_length=9,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name='статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='сообщение'
    )
    clients = models.ManyToManyField(
        Client,
        related_name='mailings',
        verbose_name='получатели'
    )
    stopped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **NULLABLE,
        related_name='stopped_mailings',
        verbose_name='остановлена пользователем',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (f'Рассылка: {self.message.title} '
                f'| {self.start_time_mailing} – {self.stop_time_mailing} '
                f'| {self.get_status_sending_display()}')

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        permissions = [
            ('can_view_all_mailings', 'Может просматривать все рассылки'),
            ('can_stop_mailing', 'Может останавливать рассылки'),
        ]


class MailingAttempt(models.Model):
    """Попытки отправки рассылок"""

    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='рассылка'
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата и время попытки'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='статус'
    )
    server_response = models.TextField(
        **NULLABLE,
        verbose_name='ответ почтового сервера'
    )

    def __str__(self):
        return f'Попытка {self.mailing.message.title} | {self.attempt_time} | {self.get_status_display()}'

    class Meta:
        verbose_name = 'попытка рассылки'
        verbose_name_plural = 'попытки рассылок'


class SchedulerState(models.Model):
    """Дата и время следующей проверки статуса рассылок"""
    next_check = models.DateTimeField(**NULLABLE)

    def __str__(self):
        return f'Следующая проверка: {self.next_check}'

    class Meta:
        verbose_name = 'состояние планировщика'
        verbose_name_plural = 'состояние планировщика'
