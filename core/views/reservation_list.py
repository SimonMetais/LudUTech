from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from ..models import Lent


@login_required
def reservation_list(request):
    today = timezone.now().date()
    lents = (Lent.objects
             .filter(borrower=request.user)
             .select_related('oeuvre', 'oeuvre__content_type')
             .order_by('-date_in')
             )
    return render(request, 'core/reservation_list.html', {
        'lents': lents,
        'today': today,
    })


@login_required
@require_POST
def cancel_reservation(request, pk):
    lent = get_object_or_404(Lent, pk=pk)
    if lent.borrower != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à annuler cette réservation.")

    today = timezone.now().date()
    if lent.date_in <= today:
        messages.error(request, "Impossible d'annuler une réservation déjà commencée ou passée.")
    else:
        lent.delete()
        messages.success(request, "Votre réservation a été annulée avec succès.")

    return redirect('reservation_list')
