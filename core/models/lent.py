from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import admin

from django.utils import timezone


class Lent(models.Model):
    """ Dates d'emprunt et infos connexes. """

    oeuvre = models.ForeignKey('Oeuvre', on_delete=models.CASCADE, verbose_name="Oeuvre")
    date_in = models.DateField(verbose_name="Date d'emprunt", db_index=True)
    date_out = models.DateField(verbose_name="Date de retour")
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lents',
        verbose_name="Emprunteur"
    )
    details = models.TextField(blank=True, verbose_name="Détails")
    returned = models.BooleanField(default=False, verbose_name="Rendu")

    def clean(self):
        super().clean()
        if not self.date_in or not self.date_out:
            return
        if self.date_in > self.date_out:
            raise ValidationError("La date de début doit être antérieure à la date de fin.")
        delta = self.date_out - self.date_in
        if delta.days > 15:
            raise ValidationError("La durée de réservation ne peut pas dépasser 15 jours.")
        if delta.days < 1:
            raise ValidationError("La durée de réservation doit être d'au moins 2 jours.")
        if {self.date_out.weekday(), self.date_in.weekday()} - {1, 3}:
            raise ValidationError("Vous ne pouvez selectionner que les mardi ou jeudi, jours d'astreinte.")
        if not self.pk and not self.returned and self.date_in < timezone.now().date():
            raise ValidationError("La date d'emprunt ne peux pas être antérieur à aujourd'hui.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    @admin.display(boolean=True, description="Retour ok")
    def return_ok(self):
        """ Indique si l'emprunt est en cours avec la date de retour passée ou aujourd'hui """
        return not (not self.returned and self.date_out <= timezone.now().date())

    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
