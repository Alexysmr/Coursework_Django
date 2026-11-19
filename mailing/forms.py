from django import forms

from clients.models import Client
from .models import Message, Mailing

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'message_body']
        labels = {
            'title': 'Тема',
            'message_body': 'Сообщение',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['message', 'clients', 'start_time_mailing', 'stop_time_mailing']
        labels = {
            'clients': 'Получатели (отметьте нужных клиентов)',
            'message': 'Сообщение',
            'start_time_mailing': 'Дата и время начала',
            'stop_time_mailing': 'Дата и время окончания',
        }
        widgets = {
            'start_time_mailing': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'stop_time_mailing': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['clients'].queryset = Client.objects.filter(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time_mailing')
        stop = cleaned_data.get('stop_time_mailing')
        if start and stop and stop <= start:
            raise forms.ValidationError('Дата окончания должна быть позже даты начала.')
        return cleaned_data
