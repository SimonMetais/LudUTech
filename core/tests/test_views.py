from django.test import TestCase, Client
from django.urls import reverse
from core.models import Game, GameType, Lent, Oeuvre, Book
import datetime

class GameViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.type = GameType.objects.create(name="Ambiance")
        self.game = Game.objects.create(
            title="Uno",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=200,
            space=Game.SpaceChoice.INDOOR
        )
        self.game.game_types.add(self.type)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uno")
        self.assertContains(response, "Bienvenue sur JDSU")

    def test_fallback_rendering(self):
        # Création d'un livre
        book = Book.objects.create(title="Le Petit Prince", author="Saint-Exupéry", nb_pages=100, isbn="123")
        
        # Le livre a un template spécifique cards/_book.html
        card_html = book.render_card()
        self.assertIn("Saint-Exupéry", card_html)
        
        # Le livre a un template spécifique details/_book.html
        detail_html = book.render_detail()
        self.assertIn("Saint-Exupéry", detail_html)
        self.assertIn("Auteur", detail_html)
        
        # Maintenant, créons une oeuvre sans template spécifique
        pure_oeuvre = Oeuvre.objects.create(title="Objet Inconnu", short_description="Description mystère")
        
        card_fallback = pure_oeuvre.render_card()
        self.assertIn("Objet Inconnu", card_fallback)
        self.assertIn("Description mystère", card_fallback)
        self.assertIn("Voir les détails", card_fallback)

    def test_game_list_view(self):
        response = self.client.get(reverse('game_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uno")

    def test_game_detail_view(self):
        # Ajout d'un ID Youtube pour tester le rendu
        self.game.video_youtube_id = "dQw4w9WgXcQ"
        self.game.save()
        
        response = self.client.get(reverse('oeuvre_detail', kwargs={'model_name': 'game', 'slug': self.game.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uno")
        # Vérifie que l'URL d'intégration est présente dans l'iframe (avec nocookie)
        self.assertContains(response, "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")
        # Vérifie la présence de referrerpolicy
        self.assertContains(response, "referrerpolicy=\"strict-origin-when-cross-origin\"")

    def test_reservation_list_view(self):
        response = self.client.get(reverse('reservation_list'))
        self.assertEqual(response.status_code, 200)

    def test_reserve_game_post_success(self):
        # Lundi 10 au Vendredi 14 Août 2026
        response = self.client.post(reverse('reserve_game', kwargs={'model_name': 'game', 'slug': self.game.slug}), {
            'borrower': 'Alice',
            'date_in': '2026-08-10',
            'date_out': '2026-08-14'
        }, follow=True)
        self.assertEqual(response.status_code, 200) 
        self.assertTrue(Lent.objects.filter(borrower='Alice').exists())
        # Utilisation de html=True ou recherche d'une partie sans accent
        self.assertContains(response, "Alice")
        self.assertContains(response, "nom de")

    def test_reserve_game_overlap(self):
        # Créer une première résa
        lent = Lent.objects.create(
            oeuvre=self.game,
            borrower='Bob',
            date_in=datetime.date(2026, 8, 10),
            date_out=datetime.date(2026, 8, 14)
        )
        # Tenter un chevauchement
        response = self.client.post(reverse('reserve_game', kwargs={'model_name': 'game', 'slug': self.game.slug}), {
            'borrower': 'Charlie',
            'date_in': '2026-08-12',
            'date_out': '2026-08-14'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dates")
        self.assertFalse(Lent.objects.filter(borrower='Charlie').exists())

    def test_reserve_game_too_long(self):
        # Tenter une résa de plus de 15 jours
        response = self.client.post(reverse('reserve_game', kwargs={'model_name': 'game', 'slug': self.game.slug}), {
            'borrower': 'Dave',
            'date_in': '2026-08-10',
            'date_out': '2026-08-30'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La durée de réservation ne peut pas dépasser 15 jours.")
        self.assertFalse(Lent.objects.filter(borrower='Dave').exists())

    def test_reserve_game_weekend(self):
        # Samedi 15 Août 2026
        response = self.client.post(reverse('reserve_game', kwargs={'model_name': 'game', 'slug': self.game.slug}), {
            'borrower': 'Eve',
            'date_in': '2026-08-15',
            'date_out': '2026-08-18'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La date de début ne peut pas être un weekend.")

    def test_game_list_play_mode_filter(self):
        from core.models import PlayMode
        coop_mode = PlayMode.objects.create(name="Coopératif")
        # Créer un jeu coopératif
        game_coop = Game.objects.create(
            title="The Crew",
            difficulty=Game.DifficultyChoice.MEDIUM,
            weight_grams=300,
            space=Game.SpaceChoice.INDOOR
        )
        game_coop.play_modes.add(coop_mode)
        
        # Test sans filtre (on doit voir les deux)
        response = self.client.get(reverse('game_list'))
        self.assertContains(response, "Uno")
        self.assertContains(response, "The Crew")
        
        # Test avec filtre play_mode
        response = self.client.get(reverse('game_list') + f"?play_mode={coop_mode.id}")
        self.assertNotContains(response, "Uno")
        self.assertContains(response, "The Crew")

    def test_game_list_ordering_by_popularity(self):
        from unittest.mock import patch
        import datetime
        from core.models import Lent
        
        # Créer un autre jeu pour tester le tri
        game_popular = Game.objects.create(
            title="Jeu Populaire",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=100
        )
        
        # Date fixe pour le test : Mardi 11 Août 2026
        now = datetime.date(2026, 8, 11)
        
        # Ajouter des emprunts récents au jeu populaire
        Lent.objects.create(
            oeuvre=game_popular,
            borrower="User1",
            date_in=now - datetime.timedelta(days=7),
            date_out=now - datetime.timedelta(days=5)
        )
        
        # Mock timezone.now().date() utilisé dans la vue
        mock_now = datetime.datetime(2026, 8, 11, 12, 0, 0, tzinfo=datetime.timezone.utc)
        with patch('django.utils.timezone.now', return_value=mock_now):
            response = self.client.get(reverse('game_list'))
            games = list(response.context['objects'])
            
            # Jeu Populaire doit être premier (1 emprunt récent)
            # Uno a 0 emprunts récents
            self.assertEqual(games[0].title, "Jeu Populaire")
            self.assertEqual(games[1].title, "Uno")

    def test_site_mode_persistence_tabs_and_filters(self):
        from unittest.mock import patch
        from core.models import CabinetColor
        color = CabinetColor.objects.create(name="Armoire Verte", color="#00FF00")
        self.game.cabinet_color = color
        self.game.save()

        # Créer un jeu réservé aujourd'hui
        game_reserved = Game.objects.create(
            title="Jeu Indisponible",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=200
        )
        today = datetime.date(2026, 8, 17)
        Lent.objects.create(
            oeuvre=game_reserved,
            borrower="Bob",
            date_in=today,
            date_out=today + datetime.timedelta(days=2),
            returned=False
        )

        mock_now = datetime.datetime(2026, 8, 17, 12, 0, 0, tzinfo=datetime.timezone.utc)
        with patch('django.utils.timezone.now', return_value=mock_now):
            # 1. Activation du mode site
            res = self.client.get(reverse('home') + "?site_mode=1")
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.context['site_mode'])
            self.assertContains(res, "checked")
            self.assertContains(res, "#00FF00")
            self.assertNotContains(res, "Jeu Indisponible")

            # 2. Changement d'onglet vers game_list (sans paramètre GET site_mode)
            res_tab = self.client.get(reverse('game_list'))
            self.assertEqual(res_tab.status_code, 200)
            self.assertTrue(res_tab.context['site_mode'])
            self.assertContains(res_tab, "checked")
            self.assertContains(res_tab, "#00FF00")
            self.assertNotContains(res_tab, "Jeu Indisponible")

            # 3. Application d'un filtre sur game_list (sans paramètre site_mode dans le formulaire)
            res_filter = self.client.get(reverse('game_list') + "?q=Uno")
            self.assertEqual(res_filter.status_code, 200)
            self.assertTrue(res_filter.context['site_mode'])
            self.assertContains(res_filter, "Uno")
            self.assertContains(res_filter, "#00FF00")

            # 4. Désactivation du mode site via ?site_mode=0
            res_off = self.client.get(reverse('home') + "?site_mode=0")
            self.assertEqual(res_off.status_code, 200)
            self.assertFalse(res_off.context['site_mode'])
            self.assertContains(res_off, "Jeu Indisponible")

            # 5. Changement d'onglet après désactivation (doit rester désactivé)
            res_tab2 = self.client.get(reverse('game_list'))
            self.assertEqual(res_tab2.status_code, 200)
            self.assertFalse(res_tab2.context['site_mode'])
            self.assertContains(res_tab2, "Jeu Indisponible")

    def test_filter_rendering_components(self):
        # 1. Page Game : contient les filtres de base (recherche) et les filtres spécifiques (difficulté, type, espace, etc.)
        res_game = self.client.get(reverse('oeuvre_list', kwargs={'model_name': 'game'}))
        self.assertEqual(res_game.status_code, 200)
        self.assertContains(res_game, 'name="q"')
        self.assertContains(res_game, 'name="type"')
        self.assertContains(res_game, 'name="difficulty"')
        self.assertContains(res_game, 'name="space"')
        self.assertContains(res_game, 'name="players"')
        self.assertContains(res_game, 'name="play_mode"')

        # 2. Page Book : pas de template spécifique, donc contient seulement le filtre de base (recherche)
        Book.objects.create(title="Dune", author="Frank Herbert", nb_pages=500, isbn="987654")
        res_book = self.client.get(reverse('oeuvre_list', kwargs={'model_name': 'book'}))
        self.assertEqual(res_book.status_code, 200)
        self.assertContains(res_book, 'name="q"')
        self.assertNotContains(res_book, 'name="type"')
        self.assertNotContains(res_book, 'name="difficulty"')
        self.assertNotContains(res_book, 'name="space"')
        self.assertNotContains(res_book, 'name="players"')
        self.assertNotContains(res_book, 'name="play_mode"')

    def test_book_query_filter(self):
        Book.objects.create(title="Dune", author="Frank Herbert", nb_pages=500, isbn="987654")
        Book.objects.create(title="Fondation", author="Isaac Asimov", nb_pages=300, isbn="123456")

        res = self.client.get(reverse('oeuvre_list', kwargs={'model_name': 'book'}) + "?q=Dune")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Dune")
        self.assertNotContains(res, "Fondation")

    def test_render_filter_templatetag(self):
        from core.templatetags.filter_tags import render_filter
        from django.template import Context, Template

        context_game = Context({'model_name': 'game'})
        filter_game = render_filter(context_game)
        self.assertIn('name="type"', filter_game)
        self.assertIn('name="difficulty"', filter_game)

        context_book = Context({'model_name': 'book'})
        filter_book = render_filter(context_book)
        self.assertEqual(filter_book, "")

        context_oeuvre = Context({'model_name': 'oeuvre'})
        filter_oeuvre = render_filter(context_oeuvre)
        self.assertEqual(filter_oeuvre, "")

        tmpl = Template("{% load filter_tags %}{% render_filter %}")
        rendered = tmpl.render(Context({'model_name': 'game'}))
        self.assertIn('name="type"', rendered)

    def test_game_query_and_specific_filters(self):
        game_catan = Game.objects.create(
            title="Catan",
            short_description="Jeu de gestion et de négociation",
            difficulty=Game.DifficultyChoice.MEDIUM,
            weight_grams=1200,
            space=Game.SpaceChoice.INDOOR,
            players_min=3,
            players_max=4
        )
        game_carcassonne = Game.objects.create(
            title="Carcassonne",
            short_description="Jeu de tuiles médiéval",
            difficulty=Game.DifficultyChoice.EASY,
            weight_grams=800,
            space=Game.SpaceChoice.INDOOR,
            players_min=2,
            players_max=5
        )

        # 1. Filtre par recherche 'q' sur titre
        res = self.client.get(reverse('oeuvre_list', kwargs={'model_name': 'game'}) + "?q=Catan")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Catan")
        self.assertNotContains(res, "Carcassonne")

        # 2. Filtre par recherche 'q' sur description
        res_desc = self.client.get(reverse('oeuvre_list', kwargs={'model_name': 'game'}) + "?q=tuiles")
        self.assertEqual(res_desc.status_code, 200)
        self.assertContains(res_desc, "Carcassonne")
        self.assertNotContains(res_desc, "Catan")

        # 3. Filtre combiné 'q' + filtre spécifique de jeu (difficulty)
        res_combo = self.client.get(
            reverse('oeuvre_list', kwargs={'model_name': 'game'}) + f"?q=Car&difficulty={Game.DifficultyChoice.EASY}"
        )
        self.assertEqual(res_combo.status_code, 200)
        self.assertContains(res_combo, "Carcassonne")
        self.assertNotContains(res_combo, "Catan")
