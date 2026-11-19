from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_active',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Profile)
