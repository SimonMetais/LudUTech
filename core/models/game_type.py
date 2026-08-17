from django.db import models


class GameType(models.Model):
    """
    Représente un type ou une catégorie de jeu (ex: Stratégie, Ambiance, Plein air).
    """
    name = models.CharField(max_length=100, verbose_name="Nom")

    class Meta:
        verbose_name = "Type de jeu"
        verbose_name_plural = "Types de jeu"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip()
        super().save(*args, **kwargs)
