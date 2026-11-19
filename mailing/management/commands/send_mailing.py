from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка рассылок'

    def add_arguments(self, parser):
        parser.add_argument('--pk', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        # Вывод списка рассылок в консоль и отправка
        from mailing.models import Mailing
        from auxiliary.services import send_mailing

        pk = options['pk']

        if pk:
            mailing = Mailing.objects.filter(pk=pk).first()
            if not mailing:
                self.stderr.write(f'Рассылка №{pk} не найдена')
                logger.warning('Command send_mailing: mailing %s not found', pk)
                return
            self.stdout.write(f'Отправка рассылки №{pk}...')
            logger.info('Command send_mailing started, pk=%s', pk)
            send_mailing(mailing)
            logger.info('Command send_mailing finished, pk=%s', pk)
            self.stdout.write(f'Отправка рассылки №{pk} завершена (см. логи)')
        else:
            self.stdout.write('Список рассылок')
            for mailing in Mailing.objects.all():
                last_attempt = mailing.attempts.last()
                last_status = last_attempt.status if last_attempt else '—'
                self.stdout.write(
                    f'{mailing.pk} | {mailing.message.title} | '
                    f'{mailing.get_status_sending_display()} | '
                    f'{mailing.stopped_by or "—"} | {last_status}'
                )
            logger.info('Command send_mailing: list requested')
            self.stdout.write('Для отправки конкретной рассылки используйте: '
                'python manage.py send_mailing --pk N\n'
                'Внимание! Выполнение рассылок со статусом started или completed '
                'приведёт к повторной отправке соответствующего сообщения клиентам указанным в этой рассылке. '
                'Выполнение рассылок со статусом created приведёт к преждевременной рассылке '
                'соответствующего сообщения без смены статуса, при наступлении периода отправки рассылка '
                'будет выполнена повторно!'
            )