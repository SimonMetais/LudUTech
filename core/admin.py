from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import Game, Book, GameType, PlayMode, Lent, Oeuvre, CabinetColor, Review

User = get_user_model()


class UserLentInline(admin.TabularInline):
    model = Lent
    extra = 0
    fields = ('oeuvre', 'date_in', 'date_out', 'date_returned', 'display_status')
    readonly_fields = ('oeuvre', 'date_in', 'date_out', 'date_returned', 'display_status')
    can_delete = False
    show_change_link = True
    ordering = ('-date_in',)

    @admin.display(description="Statut", ordering="status")
    def display_status(self, obj):
        return obj.status


if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = list(BaseUserAdmin.inlines) + [UserLentInline]
    list_display = BaseUserAdmin.list_display + ('lent_status_badge',)
    readonly_fields = BaseUserAdmin.readonly_fields + ('lent_status_summary',)

    @admin.display(description="État emprunts")
    def lent_status_badge(self, obj):
        return obj.lent_status_badge

    @admin.display(description="Statistiques d'emprunt")
    def lent_status_summary(self, obj):
        return obj.lent_status_badge

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets = fieldsets + (
                ("Historique & Fiabilité", {"fields": ("lent_status_summary",)}),
            )
        return fieldsets


@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PlayMode)
class PlayModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji')
    search_fields = ('name',)


@admin.register(CabinetColor)
class CabinetColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name', 'color')


class OeuvreBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'cabinet_color', 'barcode')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Oeuvre)
class OeuvreAdmin(OeuvreBaseAdmin):
    pass


@admin.register(Book)
class BookAdmin(OeuvreBaseAdmin):
    search_fields = ('title', 'author', 'isbn')


@admin.register(Game)
class GameAdmin(OeuvreBaseAdmin):
    list_filter = ('is_legacy', 'difficulty', 'game_types', 'play_modes', 'cabinet_color')
    search_fields = ('title', 'short_description')
    filter_horizontal = ('game_types', 'play_modes')

@admin.register(Lent)
class LentAdmin(admin.ModelAdmin):
    list_display = ('oeuvre', 'borrower', 'date_in', 'date_out', 'date_returned', 'display_status')
    list_filter = ('date_in', 'date_out', 'oeuvre')
    search_fields = ('borrower__username', 'borrower__first_name', 'borrower__last_name', 'borrower__email', 'oeuvre__title', 'details')
    ordering = ('date_returned', 'date_out')
    readonly_fields = ('oeuvre_details', 'display_status')

    @admin.display(description="Statut", ordering="status")
    def display_status(self, obj):
        return obj.status

    @admin.display(description="Détails de l'oeuvre")
    def oeuvre_details(self, obj):
        if obj.oeuvre:
            return f"{obj.oeuvre.title} ({obj.oeuvre.content_type})"
        return "-"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('oeuvre', 'user', 'rating', 'created_at', 'updated_at', 'comment')
    list_filter = ('rating', 'created_at', 'updated_at', 'oeuvre')
    search_fields = ('oeuvre__title', 'user__username', 'user__first_name', 'user__last_name', 'comment')
