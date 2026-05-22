"""
Address Admin — configuração do Django Admin para ChurchAddress e MemberAddress.
"""
from django.contrib import admin
from django.utils.html import format_html

from ..models import ChurchAddress, MemberAddress


@admin.register(ChurchAddress)
class ChurchAddressAdmin(admin.ModelAdmin):
    list_display = ("church", "full_address", "city", "state", "cep", "principal")
    list_filter = ("state", "principal")
    search_fields = ("church__user__first_name", "church__user__last_name", "road", "city", "cep")
    ordering = ("church__user__first_name", "city")
    list_per_page = 30
    readonly_fields = ("slug",)

    fieldsets = (
        (
            "Igreja",
            {"fields": ("church", "principal")},
        ),
        (
            "Endereço",
            {
                "fields": (
                    "cep",
                    ("road", "number"),
                    ("district", "city", "state"),
                    "complement",
                    "country",
                    "slug",
                ),
            },
        ),
    )

    @admin.display(description="Endereço completo")
    def full_address(self, obj):
        return str(obj)


@admin.register(MemberAddress)
class MemberAddressAdmin(admin.ModelAdmin):
    list_display = ("member", "full_address", "city", "state", "cep", "principal")
    list_filter = ("state", "principal")
    search_fields = ("member__user__first_name", "member__user__last_name", "road", "city", "cep")
    ordering = ("member__user__first_name", "city")
    list_per_page = 30
    readonly_fields = ("slug",)

    fieldsets = (
        (
            "Membro",
            {"fields": ("member", "principal")},
        ),
        (
            "Endereço",
            {
                "fields": (
                    "cep",
                    ("road", "number"),
                    ("district", "city", "state"),
                    "complement",
                    "country",
                    "slug",
                ),
            },
        ),
    )

    @admin.display(description="Endereço completo")
    def full_address(self, obj):
        return str(obj)