from django.conf import settings
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='почта')
    name = models.CharField(max_length=150, verbose_name='имя')
    patronymic = models.CharField(max_length=150, **NULLABLE, verbose_name='отчество')
    surname = models.CharField(max_length=150, verbose_name='фамилия')
    comments = models.TextField(verbose_name='комментарии')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        related_name='clients',
        verbose_name='владелец'
    )

    def __str__(self):
        return f'{self.name} {self.surname} - {self.email}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        permissions = [
            ('can_view_all_clients', 'Может просматривать всех клиентов'),
        ]
