"""
Admin Inlines — formulários inline para o admin.
"""
from django.contrib import admin
from dizimus.apps.users.models.church import ChurchAddress
from dizimus.apps.users.models.member import  MemberAddress
from dizimus.apps.community.models.member_church_model import  MemberChurch


class ChurchAddressInline(admin.StackedInline):
    model = ChurchAddress
    extra = 0
    min_num = 0
    max_num = 5
    can_delete = True
    show_change_link = True
    fields = (
        ("cep", "principal"),
        ("road", "number"),
        ("district", "city", "state"),
        "complement",
        "country",
    )
    readonly_fields = ("slug",)


class MemberAddressInline(admin.StackedInline):
    model = MemberAddress
    extra = 0
    min_num = 0
    max_num = 5
    can_delete = True
    show_change_link = True
    fields = (
        ("cep", "principal"),
        ("road", "number"),
        ("district", "city", "state"),
        "complement",
        "country",
    )
    readonly_fields = ("slug",)


class MemberChurchInline(admin.TabularInline):
    model = MemberChurch
    fk_name = "church"
    extra = 0
    can_delete = True
    show_change_link = True
    autocomplete_fields = ("member",)
    fields = ("member", "status", "joined_at", "left_at", "role")
    readonly_fields = ("joined_at",)


class MemberMembershipInline(admin.TabularInline):
    model = MemberChurch
    fk_name = "member"
    extra = 0
    can_delete = True
    show_change_link = True
    autocomplete_fields = ("church",)
    fields = ("church", "status", "joined_at", "left_at")
    readonly_fields = ("joined_at",)