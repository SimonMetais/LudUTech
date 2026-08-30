from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe


def get_user_lent_stats(self):
    """ Retourne les statistiques de ponctualité d'emprunt pour l'utilisateur. """
    from core.models.lent import Lent

    lents_qs = self.lents
    total = lents_qs.count()
    if total == 0:
        return {"total": 0, "late_count": 0, "late_rate": 0, "has_late": False}

    late_count = lents_qs.filter(status__in=[Lent.Status.RETURNED_LATE, Lent.Status.HANDED_LATE]).count()
    return {
        "total": total,
        "late_count": late_count,
        "late_rate": round((late_count / total) * 100),
        "has_late": late_count > 0,
    }


def get_user_lent_badge(self):
    """ Retourne le badge HTML stylisé représentant l'état et les statistiques d'emprunts de l'utilisateur. """
    stats = self.lent_stats
    if stats["total"] == 0:
        return mark_safe(
            '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200" '
            'style="background-color:#f3f4f6; color:#374151; padding:2px 8px; border-radius:4px; font-size:12px; border:1px solid #e5e7eb;">'
            'Aucun emprunt'
            '</span>'
        )

    plural = "s" if stats["total"] > 1 else ""
    if stats["late_rate"] > 25:
        return format_html(
            '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800 border border-red-200" '
            'style="background-color:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; border:1px solid #fecaca;">'
            '⚠️ {}% retards ({}/{})'
            '</span>',
            stats["late_rate"],
            stats["late_count"],
            stats["total"],
        )
    elif stats["late_count"] > 0:
        return format_html(
            '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200" '
            'style="background-color:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; border:1px solid #fde68a;">'
            '⚡ {}% retards ({}/{})'
            '</span>',
            stats["late_rate"],
            stats["late_count"],
            stats["total"],
        )
    else:
        return format_html(
            '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200" '
            'style="background-color:#d1fae5; color:#065f46; padding:2px 8px; border-radius:4px; font-size:12px; border:1px solid #a7f3d0;">'
            '✓ 0% retard ({} emprunt{})'
            '</span>',
            stats["total"],
            plural,
        )


User = get_user_model()
User.add_to_class('lent_stats', property(get_user_lent_stats))
User.add_to_class('lent_status_badge', property(get_user_lent_badge))
User.add_to_class('lent_badge', property(get_user_lent_badge))
