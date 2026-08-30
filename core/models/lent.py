from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.db.models import Case, When, Value, F
from django.utils import timezone


class LentManager(models.Manager):
    def get_queryset(self):
        today = timezone.now().date()
        s = Lent.Status
        return super().get_queryset().annotate(
            status=Case(
                When(date_returned__isnull=True, date_in__gt=today, then=Value(s.RESERVED)),
                When(date_returned__isnull=True, date_in=today, then=Value(s.PICKUP)),
                When(date_returned__isnull=True, date_in__lt=today, date_out__gt=today, then=Value(s.PENDING)),
                When(date_returned__isnull=True, date_out=today, then=Value(s.HANDED)),
                When(date_returned__isnull=True, date_out__lt=today, then=Value(s.HANDED_LATE)),
                When(date_in__lte=today, date_returned__lte=F('date_out'), then=Value(s.RETURNED)),
                When(date_in__lte=today, date_returned__gt=F('date_out'), then=Value(s.RETURNED_LATE)),
                default=Value(s.IMPOSSIBLE_STATE),
                output_field=models.CharField(max_length=255),
            )
        )


class Lent(models.Model):
    """ Dates d'emprunt et infos connexes. """

    class Status(models.TextChoices):
        RESERVED = "Réservé", "Réservé"
        PICKUP = "Retrait aujourd'hui", "Retrait aujourd'hui"
        PENDING = "En cours", "En cours"
        HANDED = "A remettre aujourd'hui", "A remettre aujourd'hui"
        HANDED_LATE = "non remis, en retard", "non remis, en retard"
        RETURNED = "Rendu", "Rendu"
        RETURNED_LATE = "Rendu en retard", "Rendu en retard"
        IMPOSSIBLE_STATE = "État impossible", "État impossible"

    oeuvre = models.ForeignKey('Oeuvre', on_delete=models.CASCADE, verbose_name="Oeuvre", related_name='lents')
    date_in = models.DateField(verbose_name="Date d'emprunt", db_index=True)
    date_out = models.DateField(verbose_name="Date de retour")
    date_returned = models.DateField(null=True, blank=True, verbose_name="Date du rendu")
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lents',
        verbose_name="Emprunteur"
    )
    details = models.TextField(blank=True, verbose_name="Détails")
    objects = LentManager()

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
        # if {self.date_out.weekday(), self.date_in.weekday()} - {1, 3}:
        #     raise ValidationError("Vous ne pouvez selectionner que les mardi ou jeudi, jours d'astreinte.")
        # if not self.pk and self.date_returned is None and self.date_in < timezone.now().date():
        #     raise ValidationError("La date d'emprunt ne peux pas être antérieur à aujourd'hui.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
        ordering = ['date_out', 'date_in']
