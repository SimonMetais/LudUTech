from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from core.models import Oeuvre, Lent


@staff_member_required
def scan_view(request, barcode=None):
    if barcode is None:
        barcode_input = request.GET.get('barcode', '').strip()
    else:
        barcode_input = str(barcode).strip()

    oeuvre = None
    lents = None
    error = None

    if barcode_input:
        oeuvre = Oeuvre.objects.filter(barcode=barcode_input).first()
        if not oeuvre:
            error = f"Aucun produit trouvé pour le code-barres « {barcode_input} »."
        else:
            lents = oeuvre.current_lents

    return render(request, 'core/scan.html', {
        'barcode': barcode_input,
        'oeuvre': oeuvre,
        'lents': lents,
        'error': error,
    })


@staff_member_required
@require_POST
def mark_lent_returned(request, pk):
    lent = get_object_or_404(Lent, pk=pk)
    oeuvre_title = lent.oeuvre.title
    lent.date_returned = timezone.now().date()
    lent.save(update_fields=['date_returned'])

    messages.success(request, f"L'œuvre « {oeuvre_title} » a bien été marquée comme rendue.")
    return redirect('scan_view')
