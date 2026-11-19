from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from clients.models import Client


@receiver(post_save, sender=Client)
def clear_cache_on_clients_save(sender, instance, **kwargs):
    cache.delete('index_stats_manager')

@receiver(post_delete, sender=Client)
def clear_cache_on_clients_delete(sender, instance, **kwargs):
    cache.delete('index_stats_manager')