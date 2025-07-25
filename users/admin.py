from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import RegionalPhoneNumberWidget

from .models import User


class InvitedUserInline(admin.TabularInline):
    model = User
    fk_name = 'invited_by'
    fields = ('phone', 'invite_code')
    readonly_fields = ('phone', 'invite_code')
    extra = 0
    verbose_name = "Приглашенный пользователь"
    verbose_name_plural = "Приглашенные пользователи"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    filter_horizontal = ()
    ordering = ('phone',)
    list_display = (
        'phone',
        'invite_code',
        'activated_invite_code',
        'invited_users_count',
        'created_at',
    )
    list_filter = (
        'invite_code',
        'activated_invite_code',
        'is_staff',
    )
    search_fields = (
        'phone',
        'invite_code',
        'activated_invite_code',
    )
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Инвайт-коды', {'fields': ('invite_code', 'activated_invite_code', 'invited_by')}),
        ('Важные даты', {'fields': ('last_login', 'created_at')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    formfield_overrides = {
        PhoneNumberField: {'widget': RegionalPhoneNumberWidget},
    }
    readonly_fields = ('created_at', 'last_login')
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('phone', 'password1', 'password2'),
            },
        ),
    )


    inlines = [InvitedUserInline]

    def invited_users_count(self, obj):
        return obj.invited_users.count()
    invited_users_count.short_description = 'Количество приглашенных'
