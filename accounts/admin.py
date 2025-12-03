from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone_number')
