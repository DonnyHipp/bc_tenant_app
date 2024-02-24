from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import *

Userd = get_user_model()


@admin.register(Userd)
class UserAdmin(UserAdmin):
    model = Userd
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "last_name",
                    "first_name",
                ),
            },
        ),
    )
    fieldsets = (
        (
            "Дополнительные",
            {
                "classes": ("wide",),
                "fields": (
                    "last_name",
                    "first_name",
                    "email",
                    "password",
                    "last_login",
                    "date_joined",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "is_active",
                ),
            },
        ),
    )
    list_display_links = ("email",)
    list_display = [
        "email",
    ]
    ordering = ("pk",)
    list_filter = (
        "email",
        "first_name",
        "last_name",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    save_on_top = True


admin.site.register(Message)
admin.site.register(MailingList)
admin.site.register(MesIn)
