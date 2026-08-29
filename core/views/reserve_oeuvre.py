from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from ..models import Oeuvre, Lent
from ..forms import LentForm

@login_required
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
                lent.borrower = request.user
                try:
                    lent.save()
                    messages.success(request, f"L'œuvre a été réservée au nom de {request.user.get_full_name() or request.user.username}.")
                    return redirect(oeuvre.get_absolute_url())
                except ValidationError as e:
                    if hasattr(e, 'message_dict'):
                        for field, errs in e.message_dict.items():
                            for err in errs:
                                form.add_error(field if field != '__all__' else None, err)
                    elif hasattr(e, 'messages'):
                        for err in e.messages:
                            form.add_error(None, err)
                    else:
                        form.add_error(None, str(e))
            else:
                form.add_error(None, "Cette œuvre est déjà réservée pour ces dates.")

    return render(request, 'core/reserve_oeuvre.html', {
        'oeuvre': oeuvre,
        'form': form,
        'existing_lents': Lent.objects.filter(oeuvre=oeuvre),
        'already_lents': Lent.objects.filter(oeuvre=oeuvre, date_returned__isnull=True, borrower=request.user),
        'model_name': model_name,
    })
