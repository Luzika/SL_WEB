'''
- Template tags are custom tags to use in the HTML template rendering
- Custom tags must be defined in an <app>/templatetags/<filename.py>
- Template tags can be imported in the HTML by using {% load <filename> %}
- The functions can be applied as {% <func> <arg1> <arg2> <...> %}
- In this specific case, the param_replacing tag only replace a query in URL
- All the other parts in the URL query will be preserved to handle the pargination  
'''

from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replacing(context, **kwargs):
    """
    Replace or add a query parameter in the current URL while preserving others.
    Usage: {% param_replacing page=2 sort="name" %}
    """
    request = context['request']  # Access the current request
    params = request.GET.copy()   # Copy current query parameters
    for param_name, param_value in kwargs.items():
        if param_value is None:
            params.pop(param_name, None)        # Remove parameter if value is None
        else:
            params[param_name] = param_value    # Replace or add parameter
    return f"?{urlencode(params)}"              # Return the new query string