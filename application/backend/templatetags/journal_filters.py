# backend/templatetags/journal_filters.py
from django import template

register = template.Library()

@register.filter
def mood_color(mood_value):
    color_map = {
        'excellent': 'green',
        'good': 'blue',
        'neutral': 'gray',
        'bad': 'orange',
        'terrible': 'red',
    }
    return color_map.get(mood_value, 'gray')