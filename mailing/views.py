from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
import logging
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin

from clients.models import Client
from .models import Mailing, Message, MailingAttempt, SchedulerState
from .forms import MessageForm, MailingForm
from auxiliary.services import send_mailing, check_mailing_statuses
from auxiliary.mixins import OwnerQuerysetMixin
from auxiliary.constants import CAN_VIEW_ALL_MAILINGS, CAN_STOP_MAILING

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    owner_permission = CAN_VIEW_ALL_MAILINGS
    template_name = 'mailing/index.html'
    context_object_name = 'mailing_data'
    paginate_by = 4

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at', 'status_sending')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user
        state = SchedulerState.objects.first()

        if user.has_perm(CAN_VIEW_ALL_MAILINGS) or user.is_superuser:
            stats = cache.get('index_stats_manager')
            if stats is None:
                stats = {
                'total_mailings' : Mailing.objects.count(),
                'total_attempts' : MailingAttempt.objects.count(),
                'success_attempts' : MailingAttempt.objects.filter(status='success').count(),
                'failed_attempts' : MailingAttempt.objects.filter(status='failed').count(),
                'active_mailings' : Mailing.objects.filter(
                    start_time_mailing__lte=now,
                    stop_time_mailing__gt=now,
                    status_sending='started'
                ).count(),
                'total_clients' : Client.objects.count()
                }
                cache.set('index_stats_manager', stats, 300)
            context.update(stats)
        else:
            context['total_mailings'] = Mailing.objects.filter(owner=user).count()
            context['total_attempts'] = MailingAttempt.objects.filter(mailing__owner=user).count()
            context['success_attempts'] = MailingAttempt.objects.filter(mailing__owner=user, status='success').count()
            context['failed_attempts'] = MailingAttempt.objects.filter(mailing__owner=user, status='failed').count()
            context['active_mailings'] = Mailing.objects.filter(
                owner=user,
                start_time_mailing__lte=now,
                stop_time_mailing__gt=now,
                status_sending='started'
            ).count()
            context['total_clients'] = Client.objects.filter(owner=user).count()

        context['next_check'] = state.next_check if state else None

        return context


class MessagesView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    owner_permission = CAN_VIEW_ALL_MAILINGS
    template_name = 'mailing/messages.html'
    context_object_name = 'messages_data'
    paginate_by = 5

    def get_queryset(self):
        return super().get_queryset().order_by('owner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    form_class = MessageForm
    model = Message
    template_name = 'mailing/message_create.html'

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:messages')


class MessageDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Message
    owner_permission = CAN_VIEW_ALL_MAILINGS
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'mailing/message_update.html'
    form_class = MessageForm
    context_object_name = 'message'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    context_object_name = 'message'
    success_url = reverse_lazy('mailing:messages')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        logger.info('Mailing created: id=%s, by user=%s', self.object.id, self.request.user.username)
        check_mailing_statuses()
        return response

    def get_success_url(self):
        return reverse_lazy('mailing:index')


class MailingDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Mailing
    owner_permission = CAN_VIEW_ALL_MAILINGS
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['can_stop'] = qs.filter(pk=self.object.pk).exists()
        return context


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_update.html'
    context_object_name = 'mailing'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        check_mailing_statuses()
        logger.info('Mailing updated: id=%s, by user=%s', self.object.id, self.request.user.username)
        return response

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    context_object_name = 'mailing'
    success_url = reverse_lazy('mailing:index')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        mailing_id = self.object.pk
        response = super().delete(request, *args, **kwargs)
        logger.info('Mailing deleted: id=%s, by user=%s', mailing_id, request.user.username)
        return response

class MailingSendView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
        if mailing.status_sending == 'completed':
            messages.error(request, 'Рассылка уже завершена.')
            return redirect('mailing:mailing_detail', pk=pk)
        elif mailing.status_sending == 'created':
            now = timezone.now()
            if mailing.start_time_mailing > now:
                messages.error(request, 'Время отправки этой рассылки ещё не наступило.')
                return redirect('mailing:mailing_detail', pk=pk)
        send_mailing(mailing)  # запуск отправки
        logger.info('Manual send: mailing_id=%s, by user=%s', mailing.pk, self.request.user.username)
        return redirect('mailing:mailing_detail', pk=pk)

class MailingStopView(LoginRequiredMixin, OwnerQuerysetMixin, SingleObjectMixin, View):
    model = Mailing
    owner_permission = CAN_STOP_MAILING

    def post(self, request, pk):
        mailing = self.get_object()
        if mailing.status_sending == 'completed' or mailing.stopped_by:
            messages.error(request, 'Рассылка уже завершена или остановлена.')
            return redirect('mailing:mailing_detail', pk=pk)
        mailing.status_sending = 'completed'
        mailing.stopped_by = request.user
        mailing.save()
        cache.delete('index_stats_manager')
        logger.info('Mailing=%s stopped by %s', mailing.pk, self.request.user.username)
        return redirect('mailing:mailing_detail', pk=pk)
