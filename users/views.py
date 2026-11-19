from datetime import timedelta

from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, TemplateView, ListView
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import logging


from .forms import CustomUserCreationForm, CustomPasswordResetForm
from .models import EmailConfirmation
from auxiliary.constants import CAN_SEE_USERS, CAN_BLOCK_USER, INTERVAL
from auxiliary.mixins import  ManagerRequiredMixin

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('mailing:index')

    def form_invalid(self, form):
        username = form.data.get('username')
        if username and User.objects.filter(username=username, is_active=False).exists():
            messages.warning(
                self.request,
                'Если не удаётся войти — свяжитесь с администрацией сайта в разделе «Контакты».'
            )
        return super().form_invalid(form)


class RegistrationUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = get_random_string(64)
        EmailConfirmation.objects.create(user=user, token=token, expires_at=timezone.now() + timedelta(hours=INTERVAL))

        confirm_url = self.request.build_absolute_uri(
            reverse_lazy('users:confirm_email', kwargs={'token': token})
        )

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Для подтверждения перейдите по ссылке: {confirm_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        self.request.session['user_email'] = user.email

        return redirect('users:email_sent')


class ConfirmEmailView(View):
    def get(self, request, token):
        try:
            confirmation = EmailConfirmation.objects.get(token=token)
        except EmailConfirmation.DoesNotExist:
            logger.warning(f'EmailConfirmation with token {token} does not exist')
            return render(request, 'users/email_confirm_failed.html')

        if not confirmation.expires_at or confirmation.expires_at <= timezone.now():
            logger.warning(f'EmailConfirmation with token {token} expired')
            user = confirmation.user
            confirmation.delete()
            if not user.is_active:
                logger.warning(f'Unconformed {user} is deleted')
                user.delete()
            return render(request, 'users/email_confirm_failed.html')

        user = confirmation.user
        user.is_active = True
        user.save()
        confirmation.delete()
        return redirect('login')


class EmailSentView(TemplateView):
    template_name = 'users/email_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.pop('user_email', '')
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            return super().post(request, *args, **kwargs)
        else:
            send_mail(
                subject='Восстановление пароля на сервисе рассылок',
                message=f'Вы получили это письмо, потому что попытались восстановить пароль на сайте.\n'
                        f'Если Вы не делали этого - игнорируйте это письмо\n\n'
                        f'Ваша почта {email} не найдена в базе данных сервиса.\n'
                        f'Если Вас заинтересовал наш сервис зарегистрируйтесь: http://127.0.0.1:8000/users/registration/',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return redirect('password_reset_done')

class UserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    manager_permission = CAN_SEE_USERS

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['manager_ids'] = set(
            User.objects.filter(groups__name='managers').values_list('pk', flat=True)
        )
        return context


class UserBlockView(LoginRequiredMixin, ManagerRequiredMixin, View):
    model = User
    manager_permission = CAN_BLOCK_USER

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_superuser or user.groups.filter(name='managers').exists():
            raise Http404
        user.is_active = not user.is_active
        user.save()
        return redirect('users:user_list')
