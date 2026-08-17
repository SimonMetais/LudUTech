from django.test import TestCase
from django.urls import reverse
from core.models import Game, Lent
from django.utils import timezone
import datetime
from datetime import timedelta

class GameOrderingTest(TestCase):
    def setUp(self):
        # Création de 3 jeux
        self.game_popular = Game.objects.create(title="Jeu Populaire", difficulty=1, weight_grams=100)
        self.game_medium = Game.objects.create(title="Jeu Moyen", difficulty=1, weight_grams=100)
        self.game_unpopular = Game.objects.create(title="Jeu Impopulaire", difficulty=1, weight_grams=100)
        
        # Utiliser une date fixe qui n'est pas un weekend (ex: 2026-08-11, un mardi)
        now = datetime.date(2026, 8, 11)
        
        # Emprunts pour le jeu populaire (3 emprunts récents)
        # On s'assure que les dates tombent sur des jours de semaine
        # 2026-08-11 -> Mardi
        # -7 jours -> Mardi
        # -14 jours -> Mardi
        for i in range(3):
            Lent.objects.create(
                oeuvre=self.game_popular,
                borrower=f"UserP{i}",
                date_in=now - timedelta(days=7*(i+1)),
                date_out=now - timedelta(days=7*(i+1)-2)
            )
            
        # Emprunts pour le jeu moyen (1 emprunt récent)
        Lent.objects.create(
            oeuvre=self.game_medium,
            borrower="UserM",
            date_in=now - timedelta(days=21), # Mardi
            date_out=now - timedelta(days=19) # Jeudi
        )
        
        # Emprunt ancien pour le jeu impopulaire (plus de 3 mois)
        Lent.objects.create(
            oeuvre=self.game_unpopular,
            borrower="UserU",
            date_in=now - timedelta(days=120), # Mardi (11 Aout -> 13 Avril environ)
            date_out=now - timedelta(days=118)
        )

    def test_game_list_ordering(self):
        # On va mocker timezone.now pour correspondre à notre date de test
        from django.utils import timezone
        import datetime
        from unittest.mock import patch

        mock_now = datetime.datetime(2026, 8, 11, 12, 0, 0, tzinfo=datetime.timezone.utc)
        
        with patch('django.utils.timezone.now', return_value=mock_now):
            response = self.client.get(reverse('game_list'))
            self.assertEqual(response.status_code, 200)
            
            games = list(response.context['objects'])
            
            # L'ordre attendu : Populaire (3), Moyen (1), Impopulaire (0)
            self.assertEqual(games[0].title, "Jeu Populaire")
            self.assertEqual(games[1].title, "Jeu Moyen")
            self.assertEqual(games[2].title, "Jeu Impopulaire")
