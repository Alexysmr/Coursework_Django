from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from mailing.models import Mailing


@receiver(post_save, sender=Mailing)
def clear_cache_on_mailing_save(sender, instance, **kwargs):
    cache.delete('index_stats_manager')

@receiver(post_delete, sender=Mailing)
def clear_cache_on_mailing_delete(sender, instance, **kwargs):
    cache.delete('index_stats_manager')