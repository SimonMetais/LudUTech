from django.shortcuts import render
from django.utils import timezone
from ..models import Lent

def reservation_list(request):
    today = timezone.now().date()
    lents = Lent.objects.filter(
        returned=False,
        date_out__gte=today
    ).order_by('-date_in')
    return render(request, 'core/reservation_list.html', {
        'lents': lents,
        'today': today,
    })
