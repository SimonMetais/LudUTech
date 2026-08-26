from django.db import models


class PlayMode(models.Model):
    """
    Représente un mode de jeu (ex: Coopératif, Compétitif, En équipe).
    """
    name = models.CharField(max_length=100, verbose_name="Nom")
    emoji = models.CharField(max_length=10, blank=True, verbose_name="Emoji")

    class Meta:
        verbose_name = "Mode de jeu"
        verbose_name_plural = "Jeux - mode"

    def __str__(self):
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip()
        super().save(*args, **kwargs)
