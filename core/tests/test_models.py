from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core.models import Game, GameType, Lent, Oeuvre, CabinetColor
import datetime

User = get_user_model()

class GameModelTest(TestCase):
    def setUp(self):
        self.type_str = GameType.objects.create(name=" Stratégie ")
        self.game = Game.objects.create(
            title=" Test Game ",
            difficulty=Game.DifficultyChoice.MEDIUM,
            weight_grams=1200
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
        self.user = User.objects.create_user(username="johndoe", first_name="John", last_name="Doe")
        self.game = Game.objects.create(
            title="Lent Test Game",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=500
        )

    def test_lent_validation_date_order(self):
        # date_in > date_out
        lent = Lent(
            oeuvre=self.game,
            borrower=self.user,
            date_in=datetime.date(2030, 8, 20), # Mardi
            date_out=datetime.date(2030, 8, 15)  # Jeudi précédent
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_lent_validation_max_duration(self):
        # > 15 jours (ex: 16 jours)
        lent = Lent(
            oeuvre=self.game,
            borrower=self.user,
            date_in=datetime.date(2030, 8, 20),  # Mardi
            date_out=datetime.date(2030, 9, 5) # Jeudi (+16j)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_lent_validation_astreinte_days(self):
        # Vendredi 23 Août 2030 (pas mardi ou jeudi)
        lent = Lent(
            oeuvre=self.game,
            borrower=self.user,
            date_in=datetime.date(2030, 8, 23),
            date_out=datetime.date(2030, 8, 27)
        )
        with self.assertRaises(ValidationError):
            lent.full_clean()

    def test_valid_lent(self):
        # Mardi 20 au Jeudi 22
        lent = Lent(
            oeuvre=self.game,
            borrower=self.user,
            date_in=datetime.date(2030, 8, 20),
            date_out=datetime.date(2030, 8, 22)
        )
        try:
            lent.full_clean()
            lent.save()
        except ValidationError:
            self.fail("ValidationError raised on valid lent")

    def test_lent_clean_missing_dates(self):
        # Ne doit pas lever TypeError si une ou les deux dates sont None
        lent = Lent(oeuvre=self.game, borrower=self.user, date_in=None, date_out=None)
        try:
            lent.clean()
        except TypeError:
            self.fail("Lent.clean() raised TypeError with missing dates")
