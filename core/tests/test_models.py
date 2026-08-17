from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import Game, GameType, Lent, Oeuvre, CabinetColor
import datetime

class GameModelTest(TestCase):
    def setUp(self):
        self.type_str = GameType.objects.create(name=" Stratégie ")
        self.game = Game.objects.create(
            title=" Test Game ",
            difficulty=Game.DifficultyChoice.MEDIUM,
            weight_grams=1200,
            space=Game.SpaceChoice.INDOOR
        )
        self.game.game_types.add(self.type_str)

    def test_game_str(self):
        self.assertEqual(str(self.game), "Test Game")

    def test_game_save_strips_fields(self):
        self.assertEqual(self.game.title, "Test Game")
        self.assertEqual(self.type_str.name, "Stratégie")

    def test_game_slug_generation(self):
        self.assertEqual(self.game.slug, "test-game")

    def test_game_new_fields(self):
        color = CabinetColor.objects.create(name="Red", color="#FF5733")
        game = Game.objects.create(
            title="Color and Video Game",
            difficulty=Game.DifficultyChoice.MEDIUM,
            weight_grams=1000,
            video_youtube_id="dQw4w9WgXcQ",
            cabinet_color=color
        )
        self.assertEqual(game.cabinet_color.color, "#FF5733")
        self.assertEqual(game.video_youtube_id, "dQw4w9WgXcQ")

class LentModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            title="Lent Test Game",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=500
        )

    def test_lent_validation_date_order(self):
        # date_in > date_out
        lent = Lent(
            oeuvre=self.game,
            borrower="John",
            date_in=datetime.date(2026, 8, 10),
            date_out=datetime.date(2026, 8, 5)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_lent_validation_max_duration(self):
        # > 15 jours (ex: 16 jours)
        lent = Lent(
            oeuvre=self.game,
            borrower="John",
            date_in=datetime.date(2026, 8, 3), # Lundi
            date_out=datetime.date(2026, 8, 19) # Mercredi (+16j)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_lent_validation_weekend_in(self):
        # Samedi 8 Août 2026
        lent = Lent(
            oeuvre=self.game,
            borrower="John",
            date_in=datetime.date(2026, 8, 8),
            date_out=datetime.date(2026, 8, 12)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_lent_validation_weekend_out(self):
        # Dimanche 9 Août 2026
        lent = Lent(
            oeuvre=self.game,
            borrower="John",
            date_in=datetime.date(2026, 8, 5),
            date_out=datetime.date(2026, 8, 9)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_valid_lent(self):
        # Lundi 10 au Vendredi 14
        lent = Lent(
            oeuvre=self.game,
            borrower="John",
            date_in=datetime.date(2026, 8, 10),
            date_out=datetime.date(2026, 8, 14)
        )
        try:
            lent.full_clean()
            lent.save()
        except ValidationError:
            self.fail("ValidationError raised on valid lent")
