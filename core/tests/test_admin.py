from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from core.models import Game, Lent, Oeuvre
from core.admin import LentAdmin
import datetime

User = get_user_model()

class LentAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.user = User.objects.create_user(username="testuser", first_name="Test", last_name="User")
        self.game = Game.objects.create(
            title="Weight Test Game",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=1000
        )
        self.lent = Lent.objects.create(
            oeuvre=self.game,
            borrower=self.user,
            date_in=datetime.date(2030, 8, 20),
            date_out=datetime.date(2030, 8, 22)
        )
        self.admin = LentAdmin(Lent, self.site)

    def test_oeuvre_details_display(self):
        display_value = self.admin.oeuvre_details(self.lent)
        self.assertIn("Weight Test Game", display_value)
        self.assertIn("Jeu", display_value)
