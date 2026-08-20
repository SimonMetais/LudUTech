import threading

_thread_locals = threading.local()

def get_site_mode():
    return getattr(_thread_locals, 'site_mode', False)

class SiteModeMiddleware:
    """ Injection du site_mode dans le thread local, pour l'injecter dans les QS """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'session'):
            if 'site_mode' in request.GET:
                request.session['site_mode'] = (request.GET.get('site_mode') == '1')
            site_mode = request.session.get('site_mode', False)
        else:
            site_mode = request.GET.get('site_mode') == '1'

        _thread_locals.site_mode = site_mode
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.site_mode = False
        return response
