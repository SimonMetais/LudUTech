from django import template
from django.template.loader import select_template, TemplateDoesNotExist

register = template.Library()


@register.simple_tag(takes_context=True)
def render_filter(context, model_name=None):
    if not model_name:
        model_name = context.get('model_name')
    if not model_name or model_name == 'oeuvre':
        return ""
    try:
        return select_template([f'core/components/filters/{model_name}.html']).render(context.flatten())
    except TemplateDoesNotExist:
        return ""


@register.simple_tag(takes_context=True)
def render_filters(context, model_name=None):
    return render_filter(context, model_name)
