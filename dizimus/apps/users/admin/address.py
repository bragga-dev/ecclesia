"""
Address Admin — configuração do Django Admin para ChurchAddress e MemberAddress.
"""
from django.contrib import admin
from django.utils.html import format_html

from dizimus.apps.users.models.member import MemberAddress
from dizimus.apps.users.models.church import ChurchAddress


@admin.register(ChurchAddress)
class ChurchAddressAdmin(admin.ModelAdmin):
    list_display = ("church", "full_address", "city", "state", "cep", "principal")
    list_filter = ("state", "principal")
    search_fields = ("church__full_name", "road", "city", "cep")  # ← Corrigido
    ordering = ("church__full_name", "city")  # ← Corrigido
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
    search_fields = ("member__first_name", "member__last_name", "road", "city", "cep")  # ← Corrigido
    ordering = ("member__first_name", "city")  # ← Corrigido
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