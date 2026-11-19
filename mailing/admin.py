from django.contrib import admin
from .models import Message, Mailing, MailingAttempt


admin.site.register(Message)
admin.site.register(Mailing)
admin.site.register(MailingAttempt)
