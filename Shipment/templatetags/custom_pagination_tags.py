from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Preserves current GET query string and replaces/adds given parameters.
    Usage: <a href="?{% url_replace page=page_obj.next_page_number %}">Next</a>
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            query[key] = value
        else:
            query.pop(key, None)  # Remove if value is None
    return query.urlencode()