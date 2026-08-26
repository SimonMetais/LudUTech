from django.db import models
from .oeuvre import Oeuvre


class Book(Oeuvre):
    author = models.CharField(max_length=255, verbose_name="Auteur")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    nb_pages = models.PositiveIntegerField(verbose_name="Nombre de pages")
    publisher = models.CharField(max_length=255, blank=True, verbose_name="Éditeur")

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
