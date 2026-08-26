from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    oeuvre = models.ForeignKey(
        'Oeuvre',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Oeuvre"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Utilisateur"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note"
    )
    comment = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Commentaire"
    )
    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['oeuvre', 'user'],
                name='unique_user_oeuvre_review',
                violation_error_message="Vous avez déjà laissé un avis sur cette oeuvre."
            )
        ]

    def __str__(self):
        return f"Avis ({self.rating}/10) de {self.user} sur {self.oeuvre}"
