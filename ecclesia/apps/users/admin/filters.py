"""
Admin Filters — filtros personalizados para o admin.
"""
from datetime import date
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from ecclesia.apps.community.models.member_church_model import MemberChurch


class HasPhotoFilter(SimpleListFilter):
    title = "Tem foto própria?"
    parameter_name = "has_photo"

    def lookups(self, request, model_admin):
        return (("yes", "Sim"), ("no", "Não"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(photo="").exclude(photo="default/user_img.jpg")
        if self.value() == "no":
            return queryset.filter(
                Q(photo="") | Q(photo="default/user_img.jpg") | Q(photo__isnull=True)
            )


class AgeRangeFilter(SimpleListFilter):
    title = "Faixa etária"
    parameter_name = "age_range"

    def lookups(self, request, model_admin):
        return (
            ("under18", "Menor de 18"),
            ("18_35", "18 – 35 anos"),
            ("36_60", "36 – 60 anos"),
            ("over60", "Acima de 60"),
            ("unknown", "Não informado"),
        )

    def queryset(self, request, queryset):
        today = date.today()

        def age_cutoff(years):
            return today.replace(year=today.year - years)

        v = self.value()
        if v == "under18":
            return queryset.filter(date_of_birth__gt=age_cutoff(18))
        if v == "18_35":
            return queryset.filter(
                date_of_birth__lte=age_cutoff(18),
                date_of_birth__gt=age_cutoff(35),
            )
        if v == "36_60":
            return queryset.filter(
                date_of_birth__lte=age_cutoff(35),  # <= 35 anos (nascidos há 35+ anos)
                date_of_birth__gt=age_cutoff(60),   # > 60 anos (nascidos há 60 anos)
            )
        if v == "over60":
            return queryset.filter(date_of_birth__lte=age_cutoff(60))
        if v == "unknown":
            return queryset.filter(date_of_birth__isnull=True)
        return queryset


class MembershipStatusFilter(SimpleListFilter):
    title = "Status de vínculo"
    parameter_name = "membership_status"

    def lookups(self, request, model_admin):
        from ecclesia.apps.community.models.member_church_model import MemberChurch
        return MemberChurch.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(church_memberships__status=self.value()).distinct()
        return queryset


class ChurchVerifiedFilter(SimpleListFilter):
    title = "Verificação"
    parameter_name = "verified"

    def lookups(self, request, model_admin):
        return (("yes", "Verificadas"), ("no", "Pendentes"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_verified=True)
        if self.value() == "no":
            return queryset.filter(is_verified=False)
        return queryset


class HasAsaasTokenFilter(SimpleListFilter):
    title = "Token Asaas"
    parameter_name = "has_asaas"

    def lookups(self, request, model_admin):
        return (("yes", "Configurado"), ("no", "Não configurado"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(asaas_token__isnull=True).exclude(asaas_token="")
        if self.value() == "no":
            return queryset.filter(Q(asaas_token__isnull=True) | Q(asaas_token=""))
        return queryset