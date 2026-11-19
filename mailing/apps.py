import os
import logging
from django.db import ProgrammingError, OperationalError

from django.apps import AppConfig

logger = logging.getLogger(__name__)

class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'

    def ready(self):
        try:
            from auxiliary.scheduler import scheduler
            import mailing.signals
            if os.environ.get('RUN_MAIN') and not scheduler.running:
                scheduler.start()
                logger.info('Scheduler started')
                from auxiliary.services import check_mailing_statuses
                check_mailing_statuses()
        except (ProgrammingError, OperationalError) as e:
            logger.exception('Ошибка при старте scheduler или проверке статусов!')
