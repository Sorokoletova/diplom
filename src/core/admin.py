from django.contrib import admin
from core.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    exclude = ['password']
    list_filter = ("is_staff", "is_active", "is_superuser")
    fieldsets = (
        ('User data', {
            'fields': ("username", "email", "first_name", "last_name")
        }),
        (None, {
            'fields': ("last_login", "date_joined", "is_staff", "is_active", "is_superuser")
        }),
    )
