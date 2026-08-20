from django.contrib import admin
from django.utils import timezone
from .models import Game, Book, GameType, PlayMode, Lent, Oeuvre, CabinetColor

class ReturnAlertFilter(admin.SimpleListFilter):
    title = 'Retour OK'
    parameter_name = 'return_ok'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Oui'),
            ('no', 'Non'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'yes':
            return queryset.exclude(returned=False, date_out__lte=today)
        if self.value() == 'no':
            return queryset.filter(returned=False, date_out__lte=today)
        return queryset

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


@admin.register(Oeuvre)
class OeuvreAdmin(OeuvreBaseAdmin):
    pass


@admin.register(Book)
class BookAdmin(OeuvreBaseAdmin):
    list_display = OeuvreBaseAdmin.list_display + ('author', 'isbn', 'publisher')
    search_fields = ('title', 'author', 'isbn')


@admin.register(Game)
class GameAdmin(OeuvreBaseAdmin):
    list_display = OeuvreBaseAdmin.list_display + ('min_age', 'players_min', 'players_max', 'space')
    list_filter = ('space', 'is_legacy', 'difficulty', 'game_types', 'play_modes', 'cabinet_color')
    search_fields = ('title', 'short_description')
    filter_horizontal = ('game_types', 'play_modes')

@admin.register(Lent)
class LentAdmin(admin.ModelAdmin):
    list_display = ('oeuvre', 'borrower', 'date_in', 'date_out', 'returned', 'return_ok')
    list_filter = (ReturnAlertFilter, 'returned', 'date_in', 'date_out', 'oeuvre')
    search_fields = ('borrower__username', 'borrower__first_name', 'borrower__last_name', 'borrower__email', 'oeuvre__title', 'details')
    ordering = ('returned', 'date_out')
    readonly_fields = ('oeuvre_details',)

    @admin.display(description="Détails de l'oeuvre")
    def oeuvre_details(self, obj):
        if obj.oeuvre:
            return f"{obj.oeuvre.title} ({obj.oeuvre.content_type})"
        return "-"