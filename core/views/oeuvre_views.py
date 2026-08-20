from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ..models import Oeuvre

def home(request):
    latest_oeuvres = Oeuvre.objects.filter(
        entry_date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-entry_date')
    return render(request, 'core/home.html', {
        'latest_oeuvres': latest_oeuvres,
        'welcome_message': "Bienvenue sur votre ludothèque préférée !"
    })


def oeuvre_list(request, model_name):
    # Trouver le ContentType à partir du nom dans l'URL (ex: 'game')
    ct = get_object_or_404(ContentType, model=model_name.lower())
    model_class = ct.model_class()
    return render(
        request, 'core/oeuvre_list.html',
        model_class.context_detail(request) | {'model_name': model_name.lower(), 'model_meta': model_class._meta}
    )


def oeuvre_detail(request, model_name, slug):
    ct = get_object_or_404(ContentType, model=model_name.lower())
    model_class = ct.model_class()
    obj = get_object_or_404(model_class.objects.all(), slug=slug)

    return render(request, 'core/oeuvre_detail.html', {
        'object': obj,
        'model_meta': model_class._meta,
        'model_name': model_name.lower(),
    })
