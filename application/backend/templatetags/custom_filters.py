from django import template

register = template.Library()

@register.filter
def user_type_color(user_type):
    color_map = {
        'athlete': 'blue',
        'coach': 'purple',
        'psychologist': 'indigo',
        'nutritionist': 'teal',
        'admin': 'red'
    }
    return color_map.get(user_type, 'gray')

@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)
