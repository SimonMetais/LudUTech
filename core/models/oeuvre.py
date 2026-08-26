from datetime import timedelta
from django.db import models
from django.db.models import Avg, Q
from django.db.models.functions import Round, Cast
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.utils import timezone

from core.middleware import get_site_mode



class OeuvreManager(models.Manager):
    def get_queryset(self):
        today = timezone.now().date()
        qs = super().get_queryset().select_related('content_type', 'cabinet_color')
        if get_site_mode():
            qs = qs.exclude(lent__date_in__lte=today, lent__date_out__gte=today, lent__returned=False)
        qs = qs.annotate(
            rating=Cast(Round(Avg('reviews__rating')), output_field=models.IntegerField()),
        )
        return qs


class CabinetColor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom (ex: Armoire A)")
    color = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Couleur (Hex)")

    class Meta:
        verbose_name = "Couleur d'armoire"
        verbose_name_plural = "Couleurs d'armoire"

    def __str__(self):
        return f"{self.name} ({self.color})"


class Oeuvre(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Code barre")
    short_description = models.TextField(blank=True, verbose_name="Courte description", max_length=635)
    entry_date = models.DateField(auto_now_add=True, verbose_name="Date d'entrée")
    cover_image = models.ImageField(upload_to='oeuvres/covers/', blank=True, null=True,
                                    verbose_name="Image de couverture")
    cabinet_color = models.ForeignKey(CabinetColor, on_delete=models.SET_NULL, blank=True, null=True,
                                      related_name="oeuvres", verbose_name="Couleur d'armoire")
    notes = models.TextField(blank=True, verbose_name="Notes de l'équipe", max_length=380)

    content_type = models.ForeignKey(ContentType, null=True, editable=False, on_delete=models.SET_NULL)
    objects = OeuvreManager()

    class Meta:
        verbose_name = "Oeuvre"
        verbose_name_plural = "Oeuvres"

    def save(self, *args, **kwargs):
        if not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('oeuvre_detail', kwargs={'model_name': self.content_type.model, 'slug': self.slug})

    @property
    def downcast(self):
        if (self.content_type.model == 'oeuvre') or (self.content_type.model == self._meta.model_name):
            return self
        return getattr(self, self.content_type.model)

    @property
    def type_name(self):
        return self.content_type.name

    @property
    def type_name_plural(self):
        return self.downcast._meta.verbose_name_plural

    def render_card(self):
        templates = [
            f'core/components/cards/{self.content_type.model}.html',
            'core/components/cards/oeuvre.html'
        ]
        return render_to_string('core/card_core.html', {
            'object': self.downcast,
            'component_template': templates,
            'site_mode': get_site_mode(),
        })

    def render_card_simple(self):
        """ Rendu rapide utilisant uniquement la table Oeuvre (évite les N+1) """
        return render_to_string('core/card_core.html', {
            'object': self,
            'component_template': 'core/components/cards/oeuvre.html',
            'site_mode': get_site_mode(),
        })

    def render_detail(self):
        templates = [
            f'core/components/details/{self.content_type.model}.html',
            'core/components/details/oeuvre.html'
        ]
        return render_to_string(templates, {'object': self.downcast})

    @classmethod
    def context_detail(cls, request) -> dict:
        qs = cls.objects.all()
        if query := request.GET.get('q'):
            qs = qs.filter(models.Q(title__icontains=query) | models.Q(short_description__icontains=query))
        return {'objects': qs}
