from django.contrib import admin
from django.contrib.auth.models import Group
from users.models import CustomUser

admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    ordering = ['username']
    list_display = [
        'username','get_full_name', 'email', 'date_joined',
        'is_active', 'is_staff', 'is_superuser'
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['is_active', 'is_staff', 'is_superuser']