from datetime import timedelta

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ..models import Oeuvre

def home(request):
    latest_oeuvres_qs = Oeuvre.objects.filter(
        entry_date__gte=timezone.now().date() - timedelta(days=60)
    ).order_by('-entry_date')

    paginator = Paginator(latest_oeuvres_qs, 5)
    page_number = request.GET.get('page', 1)
    latest_oeuvres_page = paginator.get_page(page_number)

    context = {
        'latest_oeuvres': latest_oeuvres_page,
        'welcome_message': "Bienvenue sur votre ludothèque préférée !"
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/home_oeuvres_items.html', context)

    return render(request, 'core/home.html', context)


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

    paginator = Paginator(obj.reviews.all(), 10)
    page_number = request.GET.get('page', 1)
    reviews_page = paginator.get_page(page_number)

    context = {
        'object': obj,
        'model_meta': model_class._meta,
        'model_name': model_name.lower(),
        'reviews': reviews_page,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/review_items.html', context)

    return render(request, 'core/oeuvre_detail.html', context)
