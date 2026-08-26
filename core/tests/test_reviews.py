from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.models import Game, Review

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", first_name="Jean", last_name="Dupont")
        self.user2 = User.objects.create_user(username="otheruser", first_name="Marie", last_name="Curie")
        self.game = Game.objects.create(title="Catan", difficulty=1, weight_grams=1000)

    def test_review_creation(self):
        review = Review.objects.create(
            oeuvre=self.game,
            user=self.user,
            rating=8,
            comment="Super jeu en famille !"
        )
        self.assertEqual(review.rating, 8)
        self.assertEqual(review.comment, "Super jeu en famille !")
        self.assertEqual(str(review), f"Avis (8/10) de {self.user} sur Catan")
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_unique_user_oeuvre_constraint(self):
        Review.objects.create(oeuvre=self.game, user=self.user, rating=7)
        with self.assertRaises(IntegrityError):
            Review.objects.create(oeuvre=self.game, user=self.user, rating=9)


class ReviewViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123", first_name="Jean", last_name="Dupont")
        self.other_user = User.objects.create_user(username="otheruser", password="password123", first_name="Marie", last_name="Curie")
        self.game = Game.objects.create(title="Catan", difficulty=1, weight_grams=1000)

    def test_review_oeuvre_login_required(self):
        url = reverse('review_oeuvre', kwargs={'model_name': 'game', 'slug': self.game.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_review_oeuvre_create_form_display(self):
        self.client.force_login(self.user)
        url = reverse('review_oeuvre', kwargs={'model_name': 'game', 'slug': self.game.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/review_form.html')
        self.assertFalse(response.context['is_edit'])
        self.assertContains(response, "Donner un avis sur")

    def test_review_oeuvre_post_create(self):
        self.client.force_login(self.user)
        url = reverse('review_oeuvre', kwargs={'model_name': 'game', 'slug': self.game.slug})
        response = self.client.post(url, {
            'rating': 9,
            'comment': 'Vraiment un classique indémodable'
        })
        self.assertRedirects(response, self.game.get_absolute_url())
        review = Review.objects.get(oeuvre=self.game, user=self.user)
        self.assertEqual(review.rating, 9)
        self.assertEqual(review.comment, 'Vraiment un classique indémodable')

    def test_review_oeuvre_automatic_edit_mode_when_review_exists(self):
        Review.objects.create(oeuvre=self.game, user=self.user, rating=6, comment="Pas mal")
        self.client.force_login(self.user)
        url = reverse('review_oeuvre', kwargs={'model_name': 'game', 'slug': self.game.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_edit'])
        self.assertContains(response, "Modifier mon avis")
        self.assertContains(response, "Pas mal")

    def test_review_oeuvre_post_update(self):
        Review.objects.create(oeuvre=self.game, user=self.user, rating=6, comment="Pas mal")
        self.client.force_login(self.user)
        url = reverse('review_oeuvre', kwargs={'model_name': 'game', 'slug': self.game.slug})
        response = self.client.post(url, {
            'rating': 10,
            'comment': 'Après plusieurs parties, c’est excellent !'
        })
        self.assertRedirects(response, self.game.get_absolute_url())
        self.assertEqual(Review.objects.filter(oeuvre=self.game, user=self.user).count(), 1)
        review = Review.objects.get(oeuvre=self.game, user=self.user)
        self.assertEqual(review.rating, 10)
        self.assertEqual(review.comment, 'Après plusieurs parties, c’est excellent !')

    def test_oeuvre_detail_button_state_and_rating(self):
        # Without user login
        url = self.game.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Donner un avis")

        # Create review by other user
        Review.objects.create(oeuvre=self.game, user=self.other_user, rating=8, comment="Super jeu")
        response = self.client.get(url)
        self.assertContains(response, "8 / 10 ⭐")
        self.assertContains(response, "Marie Curie")

        # Login as user with no review yet
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertContains(response, "Donner un avis")

        # User adds review
        Review.objects.create(oeuvre=self.game, user=self.user, rating=10, comment="Génial")
        response = self.client.get(url)
        self.assertContains(response, "Modifier mon avis")

    def test_review_list_view(self):
        self.client.force_login(self.user)
        Review.objects.create(oeuvre=self.game, user=self.user, rating=9, comment="Mon avis perso")
        Review.objects.create(oeuvre=self.game, user=self.other_user, rating=4, comment="Avis autre")

        url = reverse('review_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/review_list.html')
        self.assertContains(response, "Mon avis perso")
        self.assertNotContains(response, "Avis autre")

    def test_delete_review(self):
        review = Review.objects.create(oeuvre=self.game, user=self.user, rating=7)
        self.client.force_login(self.user)

        url = reverse('delete_review', kwargs={'pk': review.pk})
        response = self.client.post(url, {'next': reverse('review_list')})
        self.assertRedirects(response, reverse('review_list'))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_delete_review_permission_denied_for_other_user(self):
        review = Review.objects.create(oeuvre=self.game, user=self.user, rating=7)
        self.client.force_login(self.other_user)

        url = reverse('delete_review', kwargs={'pk': review.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())
