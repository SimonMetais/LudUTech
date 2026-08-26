from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from ..models import Oeuvre, Review
from ..forms import ReviewForm


@login_required
def review_oeuvre(request, model_name, slug):
    oeuvre = get_object_or_404(Oeuvre, slug=slug)
    review = Review.objects.filter(oeuvre=oeuvre, user=request.user).first()
    is_edit = review is not None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.oeuvre = oeuvre
            rev.user = request.user
            rev.save()
            if is_edit:
                messages.success(request, "Votre avis a été mis à jour avec succès.")
            else:
                messages.success(request, "Votre avis a été enregistré avec succès.")
            return redirect(oeuvre.get_absolute_url())
    else:
        form = ReviewForm(instance=review)

    return render(request, 'core/review_form.html', {
        'oeuvre': oeuvre,
        'form': form,
        'is_edit': is_edit,
        'review': review,
        'model_name': model_name,
    })


@login_required
def review_list(request):
    reviews = (Review.objects
               .filter(user=request.user)
               .select_related('oeuvre', 'oeuvre__content_type', 'oeuvre__cabinet_color')
               .order_by('-updated_at'))
    return render(request, 'core/review_list.html', {
        'reviews': reviews,
    })


@login_required
@require_POST
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cet avis.")

    oeuvre_url = review.oeuvre.get_absolute_url()
    review.delete()
    messages.success(request, "Votre avis a été supprimé avec succès.")

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(oeuvre_url)
