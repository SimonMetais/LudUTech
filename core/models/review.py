from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Review(models.Model):
    oeuvre = models.ForeignKey(
        'Oeuvre',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Oeuvre"
    )
    date = models.DateField(default=timezone.now, verbose_name="Date")
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note"
    )
    comment = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-date']

    def __str__(self):
        return f"Avis ({self.rating}/10) - {self.oeuvre}"

    # def clean(self):
    #     super().clean()
    #     if self.rating is not None and not (0 <= self.rating <= 10):
    #         raise ValidationError("La note doit être comprise entre 0 et 10.")
    #     if self.comment and len(self.comment) > 150:
    #         raise ValidationError("Le commentaire ne doit pas dépasser 150 caractères.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)
