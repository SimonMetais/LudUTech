from .models.oeuvre import Oeuvre
from .middleware import get_site_mode

def oeuvre_types(request):
    """
    Injecte les types d'oeuvres (sous-classes de Oeuvre) pour le menu ainsi que l'état du mode sur site.
    """
    subclasses = Oeuvre.__subclasses__()
    menu_items = []
    for cls in subclasses:
        menu_items.append({
            'name': cls._meta.verbose_name_plural,
            'url_name': cls._meta.model_name
        })
    return {
        'nav_oeuvres': menu_items,
        'site_mode': get_site_mode(),
    }
