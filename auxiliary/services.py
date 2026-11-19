from apscheduler.jobstores.base import JobLookupError
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Min
from django.core.cache import cache
import logging

from mailing.models import MailingAttempt, Mailing, SchedulerState
from mailing_project import settings
from .scheduler import scheduler
from .constants import JOB_ID

logger = logging.getLogger(__name__)

def send_mailing(mailing):
    """Функция отправки рассылки"""

    attempts = []
    logger.info('send_mailing: mailing_id=%s, clients=%s', mailing.id, mailing.clients.count())
    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )
            trying_send = MailingAttempt(
                mailing=mailing,
                status='success',
                server_response='OK',
            )
        except Exception as e:
            logger.warning('send_mailing: failed for %s: %s', client.email, e)
            trying_send = MailingAttempt(
                mailing=mailing,
                status='failed',
                server_response=str(e),
            )
        attempts.append(trying_send)
    if attempts:
        MailingAttempt.objects.bulk_create(attempts)
        cache.delete('index_stats_manager')
        logger.info('send_mailing: mailing_id=%s, attempts=%s', mailing.id, len(attempts))

def check_mailing_statuses():
    """Функция проверки и изменения статуса рассылки в зависимости от текущего момента времени"""
    now = timezone.now()
    logger.info('check_mailing_statuses: start')
    for mailing in Mailing.objects.filter(stopped_by__isnull=True):
        old_status = mailing.status_sending

        if mailing.start_time_mailing > now:
            new_status = 'created'
        elif mailing.stop_time_mailing <= now:
            new_status = 'completed'
        else:
            new_status = 'started'

        if old_status != new_status:
            if old_status == 'created' and new_status == 'started':
                send_mailing(mailing)
            mailing.status_sending = new_status
            mailing.save()
            logger.info('mailing %s: %s -> %s', mailing.id, old_status, new_status)

    cache.delete('index_stats_manager')
    next_check = get_next_check_time()
    logger.info('check_mailing_statuses: done, next check: %s', timezone.localtime(next_check) if next_check else None)
    schedule_next_check()


def get_next_check_time():
    """Получение ближайших даты и времени проверки статуса рассылок для передачи в APScheduler"""
    now = timezone.now()
    mailings = Mailing.objects.exclude(status_sending='completed').all()
    start_times = mailings.filter(start_time_mailing__gt=now).aggregate(Min('start_time_mailing'))
    stop_times = mailings.filter(stop_time_mailing__gt=now).aggregate(Min('stop_time_mailing'))

    candidates = [t for t in [start_times['start_time_mailing__min'], stop_times['stop_time_mailing__min']] if t]
    next_check = min(candidates) if candidates else None

    state, _ = SchedulerState.objects.get_or_create(pk=1)
    state.next_check = next_check
    state.save()
    return next_check


def schedule_next_check():
    """Перезапись триггера после срабатывания текущего"""
    state = SchedulerState.objects.get(pk=1)
    next_check = state.next_check

    if next_check:
        scheduler.add_job(
            check_mailing_statuses,
            trigger='date',
            run_date=next_check,
            id=JOB_ID,
            replace_existing=True,
        )
    else:
        try:
            scheduler.remove_job(JOB_ID)
        except JobLookupError:
            logger.info('Job %s not found, nothing to remove', JOB_ID)
