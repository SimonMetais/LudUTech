from django.apps import apps
from django.db import models
from django.db.models import Q, Count, QuerySet
from django.utils import timezone
from datetime import timedelta

from core.models import Oeuvre
from core.models.oeuvre import OeuvreManager


class GameManager(OeuvreManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('game_types', 'play_modes')


class Game(Oeuvre):
    class DifficultyChoice(models.IntegerChoices):
        EASY = 1, "Facile"
        MEDIUM = 2, "Moyen"
        HARD = 3, "Difficile"
        EXPERT = 4, "Expert"

    min_age = models.PositiveIntegerField(default=0, verbose_name="Âge minimum")
    players_min = models.PositiveIntegerField(default=0, verbose_name="Nombre de joueurs minimum")
    players_max = models.PositiveIntegerField(default=0, verbose_name="Nombre de joueurs maximum")
    game_types = models.ManyToManyField('GameType', blank=True, related_name="games", verbose_name="Types")
    weight_grams = models.PositiveIntegerField(verbose_name="Poids en état (grammes)")
    difficulty = models.PositiveSmallIntegerField(choices=DifficultyChoice.choices, verbose_name="Difficulté")
    play_time = models.PositiveIntegerField(default=0, verbose_name="Temps de jeu (minutes)")
    play_modes = models.ManyToManyField('PlayMode', blank=True, related_name="games", verbose_name="Modes de jeu")
    is_legacy = models.BooleanField(default=False, verbose_name="Legacy")
    video_youtube_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="ID Vidéo YouTube")
    box_content = models.TextField(blank=True, verbose_name="Contenue de la boite")

    objects = GameManager()

    class Meta:
        verbose_name = "Jeu"
        verbose_name_plural = "Jeux"

    @property
    def box_content_items(self):
        return [line.strip('- ') for line in self.box_content.splitlines() if line]

    @property
    def video_rules_embed_url(self):
        if not self.video_youtube_id:
            return None
        return f"https://www.youtube-nocookie.com/embed/{self.video_youtube_id}"

    def __str__(self):
        return self.title

    @classmethod
    def context_detail(cls, request):
        context = super().context_detail(request)
        games = context['objects']

        three_months_ago = timezone.now().date() - timedelta(days=90)
        games = games.annotate(
            recent_lents_count=Count(
                'lent',
                filter=Q(lent__date_in__gte=three_months_ago)
            )
        ).order_by('-recent_lents_count', '-entry_date')

        if game_type := request.GET.get('type'):
            games = games.filter(game_types__id=game_type)
        if difficulty := request.GET.get('difficulty'):
            games = games.filter(difficulty=difficulty)
        if play_mode := request.GET.get('play_mode'):
            games = games.filter(play_modes__id=play_mode)
        if (players := request.GET.get('players')) and players.isdigit():
            players_count = int(players)
            games = games.filter(players_min__lte=players_count, players_max__gte=players_count)

        context.update({
            'objects': games,
            'game_types': apps.get_model('core', 'GameType').objects.all(),
            'play_modes': apps.get_model('core', 'PlayMode').objects.all(),
            'difficulty_choices': Game.DifficultyChoice.choices,
        })
        return context
