from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

NULLABLE = {'blank' : True, 'null' : True}


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='пользователь'
    )
    patronymic = models.CharField(
        max_length=150,
        **NULLABLE,
        verbose_name='отчество'
    )
    phone = models.CharField(
        max_length=20,
        **NULLABLE,
        verbose_name='телефон'
    )

    def __str__(self):
        return f'Профиль {self.user.username}'

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'
        permissions = [
            ('can_block_user', 'Может блокировать пользователей'),
            ('can_see_users', 'Может просматривать список пользователей'),
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class EmailConfirmation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(**NULLABLE)
