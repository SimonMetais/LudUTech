from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import Oeuvre, Lent
from ..forms import LentForm

def reserve_oeuvre(request, model_name, slug):
    oeuvre = get_object_or_404(Oeuvre, slug=slug)
    form = LentForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            # Vérifier les chevauchements (en plus des validations du modèle)
            date_in = form.cleaned_data['date_in']
            date_out = form.cleaned_data['date_out']
            
            overlapping = Lent.objects.filter(
                oeuvre=oeuvre,
                date_in__lt=date_out,
                date_out__gt=date_in
            ).exists()
            
            if not overlapping:
                lent = form.save(commit=False)
                lent.oeuvre = oeuvre
                lent.save()
                messages.success(request, f"L'œuvre a été réservée au nom de {lent.borrower}.")
                return redirect(oeuvre.get_absolute_url())
            else:
                form.add_error(None, "Cette œuvre est déjà réservée pour ces dates.")

    return render(request, 'core/reserve_oeuvre.html', {
        'oeuvre': oeuvre,
        'form': form,
        'existing_lents': Lent.objects.filter(oeuvre=oeuvre),
        'model_name': model_name,
    })
